from django.contrib.gis.db import models
from django.contrib.auth.models import User


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
            template += 1
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
