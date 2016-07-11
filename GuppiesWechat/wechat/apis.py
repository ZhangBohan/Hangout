import time

from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.views.generic import View
from wechat.apps import WechatJsonResponse
from wechat.froms import *
from wechat.models import *

from qiniu import Auth, put_stream

access_key = '1H3USr1wF7hQ80AeRlq_BF0KoEnoJq2atE4UULwp'
secret_key = 'awFedibl6FB3L-4FSXG1NY4Qq3MFwiDoZcNFDKTF'

q = Auth(access_key, secret_key)
bucket_name = 'guppies'
base_url = 'http://oa3rslghz.bkt.clouddn.com/'


class LoginRequiredView(View):
    def dispatch(self, request, *args, **kwargs):
        if 'account' not in request.session:
            if settings.DEBUG:
                account = Account.objects.first()
                request.session['account'] = account.to_json()
            return HttpResponseForbidden()
        request.account = request.session['account']
        return super(LoginRequiredView, self).dispatch(request, *args, **kwargs)


class PhotosView(LoginRequiredView):
    def get(self, request):
        photos = Photo.objects.all()
        return WechatJsonResponse(photos)

    def post(self, request):
        form = UploadPhotoForm(request.POST, request.account)
        if form.is_valid():
            item = form.save()
            return WechatJsonResponse(item)
        return HttpResponseBadRequest()


class CommentsView(LoginRequiredView):

    def get(self, request, photo_id):
        comments = Comment.objects.filter(photo_id=photo_id)
        return WechatJsonResponse(comments)

    def post(self, request, photo_id):
        form = CommentForm(request.POST, request.account)
        if form.is_valid():
            comment = form.save()
            return WechatJsonResponse(comment)
        return HttpResponseBadRequest()


class VotesView(LoginRequiredView):
    def post(self, request, photo_id):
        form = VoteForm(request.POST, request.account)
        if form.is_valid():
            form.save()
            return WechatJsonResponse({})
        return HttpResponseBadRequest()

    def delete(self, request, photo_id):
        form = DeleteVoteForm(request.POST, request.account)
        if form.is_valid():
            form.save()
            return WechatJsonResponse({})
        return HttpResponseBadRequest()


class MarksView(LoginRequiredView):
    def post(self, request, photo_id):
        form = MarkForm(request.POST, request.account)
        if form.is_valid():
            form.save()
            return WechatJsonResponse({})
        return HttpResponseBadRequest()


class FileUploadView(LoginRequiredView):
    def post(self, request):
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            key = '{user_id}_{timestamp}'.format(user_id=request.account.get('id'), timestamp=time.time())
            token = q.upload_token(bucket_name, key, 3600)

            ret, info = put_stream(token, key, request.FILES['file'], file_name=key, data_size=len(request.FILES['file']))
            print(info)
            return WechatJsonResponse({"url": "{base_url}{key}".format(base_url=base_url, key=key)})
        return HttpResponseBadRequest()
