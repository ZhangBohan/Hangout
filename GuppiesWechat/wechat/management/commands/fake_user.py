from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from wechat.models import UserInfo


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not settings.DEBUG:
            print('This is only do in debug model!!!')
            return
        username = 'root'
        password = 'admin123'
        user = User.objects.create_user(username, 'root@admin.com', password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()

        ui = UserInfo.objects.create(user=user,
                                     nickname='这些年你跑哪去了',
                                     avatar_url='http://oa3rslghz.bkt.clouddn.com/12_avatar_1468845934.8256485')
        ui.save()

        print('username:', username, 'password:', password)
