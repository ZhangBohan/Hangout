from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.views.generic import View
from wechat.apps import WechatJsonResponse
from wechat.froms import *
from wechat.models import *


class LoginRequiredView(View):
    def dispatch(self, request, *args, **kwargs):
        if 'account' not in request.session:
            return HttpResponseForbidden()
        request.account = request.session['account']
        super(LoginRequiredView, self).dispatch(request, *args, **kwargs)


class PhotosView(LoginRequiredView):
    def get(self, request):
        photos = Photo.objects.all()
        return WechatJsonResponse(photos)

    def post(self, request):
        form = UploadPhotoForm(request.POST, request.account)
        if form.is_valid():
            item = form.save()
            return WechatJsonResponse(item)
        raise HttpResponseBadRequest()


class CommentsView(LoginRequiredView):

    def get(self, request, photo_id):
        comments = Comment.objects.filter(photo_id=photo_id)
        return WechatJsonResponse(comments)

    def post(self, request, photo_id):
        form = CommentForm(request.POST, request.account)
        if form.is_valid():
            comment = form.save()
            return WechatJsonResponse(comment)
        raise HttpResponseBadRequest()


class VotesView(LoginRequiredView):
    def post(self, request, photo_id):
        form = VoteForm(request.POST, request.account)
        if form.is_valid():
            form.save()
            return WechatJsonResponse({})
        raise HttpResponseBadRequest()

    def delete(self, request, photo_id):
        form = DeleteVoteForm(request.POST, request.account)
        if form.is_valid():
            form.save()
            return WechatJsonResponse({})
        raise HttpResponseBadRequest()


class MarksView(LoginRequiredView):
    def post(self, request, photo_id):
        form = MarkForm(request.POST, request.account)
        if form.is_valid():
            form.save()
            return WechatJsonResponse({})
        raise HttpResponseBadRequest()
