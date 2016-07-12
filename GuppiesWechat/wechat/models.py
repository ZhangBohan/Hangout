import json
from datetime import datetime, timedelta

from django.db.models import QuerySet

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db import models
from django.contrib.gis.db import models


class CommonModelMixin(object):
    EXCLUDE_FIELDS = ()
    INCLUDE_PROPERTIES = ()

    def permissions(self, account):
        return []

    def incr(self, field: str, count: int = 1):
        setattr(self, field, models.F(field) + count)
        return self

    def to_dict(self,
                account: 'Account' = None,
                extra_data: dict = None,
                include_properties: iter = None,
                exclude_fields: tuple = None,
                is_with_permissions: bool = False
                ) -> dict:
        data = {}

        if exclude_fields is None: exclude_fields = ()
        if hasattr(self, 'EXCLUDE_FIELDS'):
            exclude_fields += self.EXCLUDE_FIELDS

        if include_properties is None: include_properties = ()
        if hasattr(self, 'INCLUDE_PROPERTIES'):
            include_properties += self.INCLUDE_PROPERTIES

        for field in self._meta.fields:
            if exclude_fields:
                continue
            data[field.name] = getattr(self, field.name)

        for field in include_properties:
            value = getattr(self, field)
            data[field] = value() if callable(value) else value

        if is_with_permissions:
            data['permissions'] = self.permissions(account)

        if extra_data is not None:
            data.update(extra_data)
        return data


class Account(CommonModelMixin, models.Model):
    nickname = models.CharField("昵称", max_length=100)
    avatar_url = models.URLField("头像")

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nickname


class WechatAuth(CommonModelMixin, models.Model):
    """
    参数	说明

    openid	用户的标识，对当前公众号唯一
    nickname	用户的昵称
    sex	用户的性别，值为1时是男性，值为2时是女性，值为0时是未知
    city	用户所在城市
    country	用户所在国家
    province	用户所在省份
    language	用户的语言，简体中文为zh_CN
    headimgurl	用户头像，最后一个数值代表正方形头像大小（有0、46、64、96、132数值可选，0代表640*640正方形头像），用户没有头像时该项为空。若用户更换头像，原有头像URL将失效。
    subscribe_time	用户关注时间，为时间戳。如果用户曾多次关注，则取最后关注时间
    unionid	只有在用户将公众号绑定到微信开放平台帐号后，才会出现该字段。详见：获取用户个人信息（UnionID机制）
    """
    openid = models.CharField("openid", max_length=100)
    unionid = models.CharField("unionid", max_length=100)
    nickname = models.CharField("昵称", max_length=100)
    sex = models.SmallIntegerField("性别", choices=((0, "未知"), (1, "男性"), (2, "女性")))
    city = models.CharField("城市", max_length=100)
    country = models.CharField("国家", max_length=100)
    province = models.CharField("省份", max_length=100)
    language = models.CharField("语言", max_length=100)
    headimgurl = models.URLField("头像")

    access_token = models.CharField("access_token", max_length=255)
    refresh_token = models.CharField("refresh_token", max_length=255)
    expires_in = models.IntegerField("超时时间", help_text="access_token接口调用凭证超时时间，单位（秒）")

    account = models.ForeignKey("Account", null=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Photo(CommonModelMixin, models.Model):
    PERMISSION_VIEW_COMMENTS_AND_LIKES = 'VIEW_COMMENTS_AND_LIKES'

    url = models.URLField("URL")
    description = models.TextField("描述")

    account = models.ForeignKey("Account")
    location = models.PointField(blank=True, null=True)

    n_total_mark = models.BigIntegerField('总分数', default=0)
    n_account_mark = models.BigIntegerField('打分人数', default=0)

    n_account_comment = models.BigIntegerField('评论人数', default=0)
    n_account_vote = models.BigIntegerField('赞人数', default=0)

    n_total_watched = models.BigIntegerField('查看数', default=0)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description

    def to_detail_dict(self, account):
        return self.to_dict(include_properties=('is_liked', 'is_voted',), account=account, is_with_permissions=True)

    @property
    def is_liked(self) -> bool:
        return Vote.objects.filter(account_id=self.account_id).first() is not None

    @property
    def is_voted(self) -> bool:
        return Mark.objects.filter(account_id=self.account_id).first() is not None

    @property
    def is_commented(self) -> bool:
        return Comment.objects.filter(account_id=self.account_id).first() is not None

    @classmethod
    def last_week_best_photo_query(cls) -> QuerySet:
        now = datetime.now()
        last_week_start = now - timedelta(days=now.weekday() + 7)
        last_week_end = last_week_start + timedelta(days=6)
        return cls.objects.filter(created_at__in=(last_week_start, last_week_end)).order_by('-n_total_mark')

    @classmethod
    def newest_photo_query(cls) -> QuerySet:
        return cls.objects.order_by('-created_at')

    @classmethod
    def my_photo_query(cls, account_id) -> QuerySet:
        return cls.objects.filter(account_id=account_id).order_by('-created_at')

    @classmethod
    def nearby_photo_query(cls, point: Point, radius: int = 5000) -> QuerySet:
        return cls.objects.filter(point__distance_lte=(point, D(m=radius))).order_by('-distance')

    def permissions(self, account) -> list:
        permissions_list = []
        if self.is_commented or self.account_id == account.id:
            permissions_list.append(self.PERMISSION_VIEW_COMMENTS_AND_LIKES)
        return permissions_list


class Mark(CommonModelMixin, models.Model):
    account = models.ForeignKey("Account")
    photo = models.ForeignKey('Photo')
    mark = models.IntegerField("分数")

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super(Mark, self).save(*args, **kwargs)
        self.photo.incr('n_total_mark', self.mark).incr('n_account_mark').save()


class Vote(CommonModelMixin, models.Model):
    account = models.ForeignKey("Account")
    photo = models.ForeignKey('Photo')

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super(Vote, self).save(*args, **kwargs)
        self.photo.incr('n_account_vote').save()


class Comment(CommonModelMixin, models.Model):
    account = models.ForeignKey("Account")
    photo = models.ForeignKey('Photo')
    description = models.TextField("评论")

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super(Comment, self).save(*args, **kwargs)
        self.photo.incr('n_account_comment').save()

    EXCLUDE_FIELDS = ('updated_at',)
    INCLUDE_PROPERTIES = ('recently', 'fixable')
