from datetime import timedelta

from django.db import transaction
from django.contrib.gis.db import models
from django.contrib.auth.models import User

from django.utils import timezone


class Template(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, help_text="所有者")

    title = models.CharField("标题", max_length=255, help_text="标题")
    content = models.TextField("正文", blank=True, null=True, help_text="正文")
    address = models.CharField("地址", blank=True, null=True, max_length=255, help_text="地址")
    address_location = models.PointField("地址坐标", blank=True, null=True, help_text="地址坐标")
    started_date = models.DateTimeField("开始时间", help_text="开始时间")
    ended_date = models.DateTimeField("结束时间", help_text="结束时间")
    notify_me = models.IntegerField("何时通知我", default=0, help_text="何时通知我")
    notify_other = models.IntegerField("何时通知别人", default=0, help_text="何时通知别人")

    used_count = models.IntegerField("模板使用次数", default=1, help_text="模板使用次数")


class Schedule(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, help_text="所有者")

    title = models.CharField("标题", max_length=255, help_text="标题")
    content = models.TextField("正文", blank=True, null=True, help_text="正文")
    address = models.CharField("地址", blank=True, null=True, max_length=255, help_text="地址")
    address_location = models.PointField("地址坐标", blank=True, null=True, help_text="地址坐标")
    started_date = models.DateTimeField("开始时间", help_text="开始时间")
    ended_date = models.DateTimeField("结束时间", help_text="结束时间")
    notify_me = models.IntegerField("何时通知我", default=0, help_text="何时通知我")
    notify_other = models.IntegerField("何时通知别人", default=0, help_text="何时通知别人")

    is_notified = models.BooleanField("是否已通知", help_text="是否已通知", default=False)
    accepted_count = models.IntegerField("模板使用次数", default=1, help_text="模板使用次数")

    def save(self, *args, **kwargs):
        template, created = Template.objects.get_or_create(title=self.title, user=self.user, defaults={
            "address": self.address,
            "address_location": self.address_location,
            "started_date": self.started_date,
            "ended_date": self.ended_date,
            "notify_me": self.notify_me,
            "notify_other": self.notify_other
        })

        if not created:
            template.used_count += 1
            template.save()
        return super(Schedule, self).save(*args, **kwargs)


class ScheduleUser(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, help_text="所有者")

    schedule = models.ForeignKey(Schedule, help_text="事件")
    is_accepted = models.BooleanField("是否接受", help_text="是否接受", default=True)

    def save(self, *args, **kwargs):
        item = super(ScheduleUser, self).save(*args, **kwargs)
        self.schedule.accepted_count += 1
        return item


QR_MAX_EXPIRE_SECONDS = 2592000  # 30天


class ScheduleShare(models.Model):

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, help_text="所有者")
    schedule = models.ForeignKey(Schedule, help_text="事件")
    ticket = models.CharField(max_length=255, help_text="获取的二维码ticket，凭借此ticket可以在有效时间内换取二维码。")
    url = models.CharField(max_length=255, help_text="二维码图片解析后的地址，开发者可根据该地址自行生成需要的二维码图片")
    expire_at = models.DateTimeField(help_text="过期时间, 默认当前时间+30天", null=True)

    @property
    def qr_url(self):
        return 'https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=' + self.ticket

    @classmethod
    @transaction.atomic
    def get_schedule_share(cls, schedule) -> "ScheduleShare":
        ss, created = cls.objects.get_or_create(user=schedule.user, schedule=schedule)
        if created or (ss.expire_at > timezone.now()):
            ss = ss.create_qr()

        return ss

    def create_qr(self):

        from django.conf import settings
        result = settings.WECHAT_BASIC.create_qrcode({
            "expire_seconds": QR_MAX_EXPIRE_SECONDS,
            "action_name": "QR_SCENE",
            "action_info": {
                "scene": {"scene_id": self.id}
            }
        })
        self.url = result.get("url")
        self.ticket = result.get("ticket")
        self.expire_at = self.created_at + timedelta(days=30)
        self.save()
        return self
