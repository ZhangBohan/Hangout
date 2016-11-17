from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from hangout.models import Schedule


class Command(BaseCommand):
    def handle(self, *args, **options):
        now = datetime.now()
        for schedule in Schedule.objects.filter(started_date__lt=now, is_notified=False).all():

            # FIXME wechat notify
            settings.WECHAT_BASIC.send_template_message(user_id=schedule.wechatauth.openid,
                                                        template_id=settings.WECHAT_NOTIFY_TEMPLATE_ID,
                                                        data={
                                                            'first': "恭喜你预约成功!",
                                                            'keyword1': schedule.title,
                                                            'keyword2': "已预约",
                                                            'keyword3': now.strftime('%Y年%m月%d日 %H时%M分'),
                                                            'remark': '',
                                                        })
            schedule.is_notified = True
            schedule.save()
