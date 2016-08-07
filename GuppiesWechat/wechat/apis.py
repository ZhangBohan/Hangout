import time

from django.http import Http404
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from wechat.models import *
from wechat.serializers import *
from rest_framework import status
from rest_framework import permissions

from qiniu import Auth, put_stream

access_key = '1H3USr1wF7hQ80AeRlq_BF0KoEnoJq2atE4UULwp'
secret_key = 'awFedibl6FB3L-4FSXG1NY4Qq3MFwiDoZcNFDKTF'

q = Auth(access_key, secret_key)
bucket_name = 'guppies'
base_url = 'http://oa3rslghz.bkt.clouddn.com/'


class CommentListView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(photo_id=self.kwargs['photo_id'])

    def get(self, request, *args, **kwargs):
        """
        评论列表
        ---
        serializer: CommentSerializer
        many: true
        """
        return super(CommentListView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        提交评论
        ---
        serializer: CommentSerializer
        many: false
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(photo_id=kwargs.get('photo_id'), user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VotesView(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_object(self, pk):
        try:
            return Photo.objects.get(pk=pk)
        except Photo.DoesNotExist:
            raise Http404

    def post(self, request, photo_id):
        """
        点赞
        ---
        """
        photo = self.get_object(photo_id)

        Vote.objects.get_or_create(photo=photo, user=request.user)

        return Response({})

    def delete(self, request, photo_id):
        """
        取消点赞
        ---
        """
        photo = self.get_object(photo_id)
        vote = Vote.objects.get(photo=photo, user=request.user)
        vote.delete()
        return Response({})


class FavoritesView(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_object(self, pk):
        try:
            return Photo.objects.get(pk=pk)
        except Photo.DoesNotExist:
            raise Http404

    def post(self, request, photo_id):
        """
        收藏
        ---
        """
        photo = self.get_object(photo_id)

        Favorite.objects.get_or_create(photo=photo, user=request.user)

        return Response({})

    def delete(self, request, photo_id):
        """
        取消收藏
        ---
        """
        photo = self.get_object(photo_id)
        favorite = Favorite.objects.get(photo=photo, user=request.user)
        favorite.delete()
        return Response({})


class MarksView(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_object(self, pk):
        try:
            return Photo.objects.get(pk=pk)
        except Photo.DoesNotExist:
            raise Http404

    def post(self, request, photo_id):
        """
        打分
        ---
        serializer: MarkSerializer
        many: false
        """
        photo = self.get_object(photo_id)

        serializer = MarkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(photo=photo, user=request.user)
            return Response({})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QiniuTokenView(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    parser_classes = (FileUploadParser,)

    def post(self, request):
        """
        取得token
        ---
        type:
          key:
            required: true
            type: string
          url:
            required: false
            type: url
          token:
            required: true
            type: string
        """
        key = '{user_id}_{timestamp}'.format(user_id=request.user.id, timestamp=time.time())
        token = q.upload_token(bucket_name, key, 3600)

        return Response({
            "token": token,
            "key": key,
            "url": "{base_url}{key}".format(base_url=base_url, key=key)
        })


class MinePhotoView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    serializer_class = PhotoSerializer

    def get_queryset(self):
        order = self.request.query_params.get('order', 'default')
        query = Photo.objects.filter(user=self.request.user).all()
        if order in ['n_account_vote', 'n_total_mark']:
            query = query.order_by('-' + order)
        return query

    def get(self, request, *args, **kwargs):
        """
        照片列表
        ---
        serializer: PhotoSerializer
        many: true
        parameters:
            - name: order
              description: 排序方式
              type: string
              paramType: query
              enum:
              - default
              - n_account_vote
              - n_total_mark
        """

        return super(MinePhotoView, self).get(request, *args, **kwargs)


class PhotoListView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer

    def get(self, request, *args, **kwargs):
        """
        照片列表
        ---
        serializer: PhotoSerializer
        many: true
        """
        return super(PhotoListView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        添加照片
        ---
        serializer: PhotoSerializer
        many: false
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhotoDetailView(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_object(self, pk):
        try:
            return Photo.objects.get(pk=pk)
        except Photo.DoesNotExist:
            raise Http404

    def get_object_for_change(self, request, pk):
        photo = self.get_object(pk)
        if photo.user != request.user:
            raise PermissionDenied()
        return photo

    def get(self, request, pk, format=None):
        """
        取得照片
        ---
        serializer: PhotoSerializer
        many: false
        """
        photo = self.get_object(pk)
        serializer = PhotoDetailSerializer(photo)
        response = Response(serializer.data)
        photo.incr('n_total_watched').save()  # 观看数加1
        return response

    def put(self, request, pk, format=None):
        """
        更新照片
        ---
        serializer: PhotoSerializer
        many: false
        """
        photo = self.get_object_for_change(request, pk=pk)
        serializer = PhotoDetailSerializer(photo, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        """
        删除照片
        ---
        serializer: PhotoSerializer
        many: false
        """
        photo = self.get_object_for_change(request, pk=pk)
        photo.delete()
        return Response()


class VoteUsersView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        photo = Photo.objects.get(pk=self.kwargs['photo_id'])
        return Vote.objects.filter(photo=photo).all()

    def get(self, request, *args, **kwargs):
        """
        赞用户列表
        ---
        parameters:
            - name: page
              description: 页数
              type: integer
              paramType: query
              default: 1
            - name: page_size
              description: 每页个数
              type: integer
              paramType: query
              default: 20

        """
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        users = []
        for vote in page:
            users.append(vote.user)

        serializer = self.get_serializer(users, many=True)
        return self.get_paginated_response(serializer.data)


class LoginUserView(APIView):
    def get(self, request):
        """
        取得我的信息
        ---
        serializer: UserSerializer

        """
        if isinstance(request.user, AnonymousUser):
            data = {
                'login_url': '/auth'
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
