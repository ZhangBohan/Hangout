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
                                                        url="https://www.speedx.com",
                                                        data={
                                                            'first': {
                                                                "value": "恭喜你预约成功!",
                                                                "color":"#173177"
                                                            },
                                                            'keyword1': {
                                                                "value": "标题",
                                                                "color":"#173177"
                                                            },
                                                            'keyword2': {
                                                                "value": "已预约",
                                                                "color":"#173177"
                                                            },
                                                            'keyword3': {
                                                                "value": '%Y年%m月%d日 %H时%M分',
                                                                "color":"#173177"
                                                            },
                                                            'remark': {
                                                                "value": 'laasljflsadkfjbalablab',
                                                                "color":"#173177"
                                                            },
                                                        })
            schedule.is_notified = True
            schedule.save()
