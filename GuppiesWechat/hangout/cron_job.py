from django.conf import settings
from django_cron import CronJobBase, Schedule as CronSchedule
from django.utils import timezone

from hangout.models import Schedule


class HangoutCronJob(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = CronSchedule(run_every_mins=RUN_EVERY_MINS)
    code = 'HangoutCronJob'  # a unique code

    def do(self):
        print('start HangoutCronJob')
        now = timezone.now()
        schedules = Schedule.objects.filter(started_date__lt=now, is_notified=False).all()
        print('schedules: ', len(schedules))
        for schedule in schedules:
            print('current schedule is: %s' % schedule)
            # wechat notify
            settings.WECHAT_BASIC.send_template_message(user_id=schedule.wechatauth.openid,
                                                        template_id=settings.WECHAT_TODO_TEMPLATE_ID,
                                                        data={
                                                            'first': {
                                                                "value": "别忘了今天的预约哦!",
                                                                "color": "#173177"
                                                            },
                                                            'keyword1': {
                                                                "value": schedule.title,
                                                                "color": "#173177"
                                                            },
                                                            'keyword2': {
                                                                "value": schedule.started_date.strftime(
                                                                    '%Y年%m月%d日 %H时%M分'),
                                                                "color": "#173177"
                                                            },
                                                            'remark': {
                                                                "value": schedule.content,
                                                                "color": "#173177"
                                                            },
                                                        })
            schedule.is_notified = True
            schedule.save()

        print('end HangoutCronJob')
