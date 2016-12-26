from datetime import timedelta

from django_cron import CronJobBase, Schedule as CronSchedule
from django.utils import timezone
from wechat_sdk import WechatBasic

from hangout import logic as hangout_logic
from hangout.models import Schedule, ScheduleUser, HangoutConfig


class HangoutCronJob(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = CronSchedule(run_every_mins=RUN_EVERY_MINS)
    code = 'HangoutCronJob'  # a unique code

    def do(self):
        print('start HangoutCronJob')
        cursor_date = timezone.now() + timedelta(hours=1)   # 取一小时内的数据
        end_date = timezone.now() - timedelta(days=1)
        schedule_users = ScheduleUser.objects.filter(notify_at__lt=cursor_date,
                                                     notify_at__gt=end_date,
                                                     is_notified=False
                                                     ).all()
        print('schedule_users: ', len(schedule_users))

        wechat_base = WechatBasic(conf=HangoutConfig.get_wechat_config())

        for schedule_user in schedule_users:
            notify_at = schedule_user.notified_date
            is_notify = notify_at < timezone.now()

            schedule = schedule_user.schedule
            print('current schedule is: %s' % schedule)
            if not is_notify:
                print('will be notify at: %s' % notify_at)
                continue

            natural_time = hangout_logic.natural_time(schedule.started_date)
            print('natural_time is: %s' % natural_time)

            text = "别忘了%s的预约哦!" % natural_time
            hangout_logic.template_notify(wechat_base, schedule.wechatauth, schedule, title=text)

            print('schedule send to owner ok')

            text = "别忘了与%s%s的预约哦!" % (schedule.user.userinfo.nickname, natural_time)
            hangout_logic.template_notify(wechat_base, schedule_user.wechatauth, schedule, title=text)
            schedule_user.is_notified = True
            schedule_user.notified_date = timezone.now()
            schedule_user.save()
            print('schedule send to other ok')
        print('end HangoutCronJob')
