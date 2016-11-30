from datetime import timedelta

import requests
from django.conf import settings
from django.db import transaction
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.db.models import F

from django.utils import timezone
from wechat_sdk import WechatBasic
from wechat_sdk import WechatConf


class Template(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, help_text="所有者")

    title = models.CharField("标题", max_length=255, help_text="标题")
    content = models.TextField("正文", blank=True, null=True, help_text="正文")
    address = models.CharField("地址", blank=True, null=True, max_length=255, help_text="地址")
    address_location = models.PointField("地址坐标", blank=True, null=True, help_text="地址坐标")
    duration = models.IntegerField("用时", default=0, help_text="用时，单位分钟")

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

    accepted_count = models.IntegerField("已接受人数", default=1, help_text="已接受人数")

    @property
    def is_past(self):
        return timezone.now() > self.started_date

    @property
    def wechatauth(self):
        from wechat.models import WechatAuth
        return WechatAuth.objects.get(user=self.user)

    @property
    def nickname(self):
        return self.user.userinfo.nickname

    def __str__(self):
        return "ID: %s, title: %s" % (self.id, self.title)

    @transaction.atomic
    def save(self, *args, **kwargs):

        item = super(Schedule, self).save(*args, **kwargs)

        schedule_user, created = ScheduleUser.objects.get_or_create(schedule=self, user=self.user)
        if not created:
            return item

        template, created = Template.objects.get_or_create(title=self.title, user=self.user, defaults={
            "content": self.content,
            "address": self.address,
            "address_location": self.address_location,
            "duration": (self.ended_date - self.started_date).total_seconds() / 60
        })

        if not created:
            template.used_count += 1
            template.save()

        return item


class ScheduleUser(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, help_text="所有者")

    schedule = models.ForeignKey(Schedule, help_text="事件")
    is_accepted = models.BooleanField("是否接受", help_text="是否接受", default=True)
    is_notified = models.BooleanField("是否已通知", help_text="是否已通知", default=False)
    notified_date = models.DateTimeField("通知时间", null=True, help_text="通知时间的记录")

    @property
    def wechatauth(self):
        from wechat.models import WechatAuth
        return WechatAuth.objects.get(user=self.user)


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
    def get_schedule_share(cls, schedule, user=None) -> "ScheduleShare":
        user = user if user else schedule.user
        ss, created = cls.objects.get_or_create(user=user, schedule=schedule)
        if created or (ss.expire_at < timezone.now()):
            ss = ss.create_qr()

        return ss

    def create_qr(self):

        wechat_base = WechatBasic(conf=HangoutConfig.get_wechat_config())
        result = wechat_base.create_qrcode({
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


class HangoutConfig(models.Model):
    ACCESS_TOKEN_KEY = 'access_token'

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    key = models.CharField("key", max_length=255, help_text="key", unique=True)
    desc = models.CharField("描述", max_length=255, help_text="描述", null=True)
    content = models.TextField("正文", blank=True, null=True, help_text="正文")

    @classmethod
    def _get_access_token(cls):
        expire_second = 3000

        expired_at = timezone.now() - timedelta(seconds=expire_second)
        config = cls.objects.filter(key=cls.ACCESS_TOKEN_KEY).first()
        if not config or config.updated_at < expired_at:
            response_json = requests.get(
                url="https://api.weixin.qq.com/cgi-bin/token",
                params={
                    "grant_type": "client_credential",
                    "appid": settings.WECHAT_APPID,
                    "secret": settings.WECHAT_APPSECRET,
                }
            )
            print('get access_token_dict from wechat')
            access_token = response_json.json().get('access_token')
            access_token_expires_at = expire_second
            cls.objects.update_or_create(key=cls.ACCESS_TOKEN_KEY,
                                         defaults={
                                             "content": access_token
                                         })
        else:
            access_token = config.content
            access_token_expires_at = (config.updated_at - expired_at).seconds
            print('get access_token from config. access_token_expires_at: %s' % access_token_expires_at)

        return {
            "access_token_expires_at": access_token_expires_at,
            "access_token": access_token
        }

    @classmethod
    def get_wechat_config(cls):
        conf = WechatConf(
            token=settings.WECHAT_TOKEN,
            appid=settings.WECHAT_APPID,
            appsecret=settings.WECHAT_APPSECRET,
            encrypt_mode='normal',  # 可选项：normal/compatible/safe，分别对应于 明文/兼容/安全 模式
            access_token_getfunc=cls._get_access_token().get('access_token'),
        )

        return conf
