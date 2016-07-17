import time

from django.http import Http404
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from wechat.models import *
from rest_framework import generics
from wechat.serializers import PhotoSerializer, CommentSerializer, MarkSerializer, PhotoDetailSerializer
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

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(photo_id=kwargs.get('photo_id'))
        return super(CommentListView, self).get(request, args, kwargs)

    def post(self, request, *args, **kwargs):
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
        photo = self.get_object(photo_id)

        Vote.objects.get_or_create(photo=photo, user=request.user)

        return Response({})

    def delete(self, request, photo_id):
        photo = self.get_object(photo_id)
        vote = Vote.objects.get(photo=photo, user=request.user)
        vote.delete()
        return Response({})


class MarksView(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_object(self, pk):
        try:
            return Photo.objects.get(pk=pk)
        except Photo.DoesNotExist:
            raise Http404

    def post(self, request, photo_id):
        photo = self.get_object(photo_id)

        serializer = MarkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(photo=photo, user=request.user)
            return Response({})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileUploadView(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    parser_classes = (FileUploadParser,)

    def post(self, request, format=None):
        key = '{user_id}_{timestamp}'.format(user_id=request.user.id, timestamp=time.time())
        token = q.upload_token(bucket_name, key, 3600)

        return Response({
            "token": token,
            "key": key,
            "url": "{base_url}{key}".format(base_url=base_url, key=key)
        })


class PhotoListView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer

    def post(self, request, *args, **kwargs):
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
        photo = self.get_object(pk)
        serializer = PhotoDetailSerializer(photo)
        response = Response(serializer.data)
        photo.incr('n_total_watched').save()  # 观看数加1
        return response

    def put(self, request, pk, format=None):
        photo = self.get_object_for_change(request, pk=pk)
        serializer = PhotoDetailSerializer(photo, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        photo = self.get_object_for_change(request, pk=pk)
        photo.delete()
        return Response()
