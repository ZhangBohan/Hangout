from django.http import JsonResponse
from django.views.generic import View
from wechat.models import *


class CommitsView(View):
    model = Commit

    def get(self, request, photo_id):
        commits = Commit.objects.filter(photo_id=photo_id).all()
        return JsonResponse([commit.to_json() for commit in commits], safe=False)
