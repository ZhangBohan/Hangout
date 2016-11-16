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
            # FIXME wechat notify
            settings.WECHAT_BASIC.send_template_message(user_id=schedule.wechatauth.openid,
                                                        template_id=settings.WECHAT_NOTIFY_TEMPLATE_ID,
                                                        data={
                                                            'title': schedule.title,
                                                            'content': schedule.content,
                                                            'address': schedule.address,
                                                            'started_date': schedule.started_date,
                                                        })
            schedule.is_notified = True
            schedule.save()

        print('end HangoutCronJob')
