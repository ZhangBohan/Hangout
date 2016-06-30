from django.views.generic import View
from wechat.apps import WechatJsonResponse
from wechat.models import *


class CommitsView(View):
    model = Commit

    def get(self, request, photo_id):
        commits = Commit.objects.filter(photo_id=photo_id).all()
        return WechatJsonResponse(commits)


