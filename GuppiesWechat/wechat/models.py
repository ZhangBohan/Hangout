from datetime import datetime, timedelta

from django.contrib.auth.models import User, AnonymousUser
from django.contrib.postgres.fields import JSONField
from django.db.models import QuerySet

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db import models
from django.contrib.gis.db import models

from .utils import gaode_location


class CommonModelMixin(object):

    def permissions(self, account):
        return []

    def safe_incr(self, field: str, count: int = 1):
        setattr(self, field, models.F(field) + count)
        return self

    def incr(self, field: str, count: int = 1):
        setattr(self, field, getattr(self, field) + count)
        return self


class UserInfo(CommonModelMixin, models.Model):
    user = models.OneToOneField(User)
    nickname = models.CharField("昵称", max_length=100, help_text="昵称")
    avatar_url = models.URLField("头像", help_text="头像")
    n_photo = models.IntegerField(default=0, help_text="我的照片数")
    n_total_mark = models.BigIntegerField(default=0, help_text="我的总得分数")
    n_vote = models.BigIntegerField(default=0, help_text="我的总赞数")
    n_favorite = models.BigIntegerField('收藏数', default=0, help_text="收藏数")

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nickname


class UserLocation(CommonModelMixin, models.Model):
    user = models.OneToOneField(User)

    location = models.PointField(blank=True, null=True)
    city = models.CharField("城市", max_length=100, null=True)
    district = models.CharField("区", max_length=100, null=True)
    province = models.CharField("省份", max_length=100, null=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        if self.location and self.location.x and self.location.y:
            province, city, district = gaode_location(self.location.x, self.location.y)
            if province:
                self.province = province
                self.city = city
                self.district = district

        user_location = super(UserLocation, self).save(*args, **kwargs)
        return user_location


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
    openid = models.CharField("openid", max_length=100, unique=True)
    unionid = models.CharField("unionid", max_length=100, unique=True)
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

    user = models.ForeignKey(User, null=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nickname


class Photo(CommonModelMixin, models.Model):
    PUBLISH_STATUS = 0
    DELETE_STATUS = -1
    STATUS_CHOICES = (
        (PUBLISH_STATUS, 'publish'),
        (DELETE_STATUS, 'delete'),
    )

    url = JSONField("URL", help_text="urls json 列表")
    description = models.TextField("描述", help_text="描述")

    user = models.ForeignKey(User, help_text="所有者")
    location = models.PointField(blank=True, null=True)
    city = models.CharField("城市", max_length=100, null=True)
    district = models.CharField("区", max_length=100, null=True)
    province = models.CharField("省份", max_length=100, null=True)

    n_total_mark = models.BigIntegerField('总分数', default=0, help_text="总分数")
    n_account_mark = models.BigIntegerField('打分人数', default=0, help_text="打分人数")
    n_avg_mark = models.BigIntegerField('平均分', default=0, help_text='平均分')

    n_account_comment = models.BigIntegerField('评论人数', default=0, help_text="评论人数")
    n_account_vote = models.BigIntegerField('赞人数', default=0, help_text="赞人数")

    n_total_watched = models.BigIntegerField('查看数', default=0, help_text="查看数")

    n_favorite = models.BigIntegerField('收藏数', default=0, help_text="收藏数")

    status = models.SmallIntegerField('状态', default=PUBLISH_STATUS,
                                      choices=STATUS_CHOICES,
                                      help_text="状态")

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at', )

    def __str__(self):
        return self.description

    def save(self, *args, **kwargs):
        self.province = self.user.userlocation.province
        self.city = self.user.userlocation.city
        self.district = self.user.userlocation.district
        self.location = self.user.userlocation.location

        photo = super(Photo, self).save(*args, **kwargs)
        self.user.userinfo.incr('n_photo').save()
        return photo

    def delete(self, using=None, keep_parents=False):
        self.status = self.DELETE_STATUS
        self.save()
        self.user.userinfo.incr('n_photo', -1).save()

    def to_detail_dict(self, account):
        return self.to_dict(include_properties=('is_liked', 'is_voted',), account=account, is_with_permissions=True)

    @property
    def is_one_url(self):
        return len(self.url) == 1

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
    def my_photo_query(cls, user_id) -> QuerySet:
        return cls.objects.filter(user_id=user_id).order_by('-created_at')

    @classmethod
    def nearby_photo_query(cls, point: Point, radius: int = 5000) -> QuerySet:
        return cls.objects.filter(point__distance_lte=(point, D(m=radius))).order_by('-distance')

    @staticmethod
    def mark_choices():
        return [i for i in range(100)]

    def is_user_voted(self, user_id):
        return Vote.objects.filter(user_id=user_id, photo=self).first() is not None

    def is_user_marked(self, user_id):
        return Mark.objects.filter(user_id=user_id, photo=self).first() is not None

    def is_user_commented(self, user_id):
        return Comment.objects.filter(user_id=user_id, photo=self).first() is not None


class Mark(CommonModelMixin, models.Model):
    user = models.ForeignKey(User)
    photo = models.ForeignKey('Photo')
    mark = models.IntegerField("分数")

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        mark = super(Mark, self).save(*args, **kwargs)

        self.photo.incr('n_total_mark', self.mark).incr('n_account_mark')
        self.photo.n_avg_mark = self.photo.n_total_mark / self.photo.n_account_mark
        self.photo.save()

        self.photo.user.userinfo.incr('n_total_mark', self.mark).save()
        return mark


class Vote(CommonModelMixin, models.Model):
    user = models.ForeignKey(User)
    photo = models.ForeignKey('Photo')

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        vote = super(Vote, self).save(*args, **kwargs)
        self.photo.incr('n_account_vote').save()
        self.photo.user.userinfo.incr('n_vote').save()
        return vote

    def delete(self, using=None, keep_parents=False):
        super(Vote, self).delete(using, keep_parents)
        self.photo.incr('n_account_vote', -1).save()
        self.photo.user.userinfo.incr('n_vote', -1).save()


class Comment(CommonModelMixin, models.Model):
    user = models.ForeignKey(User)
    photo = models.ForeignKey('Photo')
    description = models.TextField("评论")

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        comment = super(Comment, self).save(*args, **kwargs)
        self.photo.incr('n_account_comment').save()
        return comment

    class Meta:
        ordering = ('-created_at', )

    def __str__(self):
        return self.description


class Favorite(CommonModelMixin, models.Model):
    user = models.ForeignKey(User)
    photo = models.ForeignKey('Photo')

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        instance = super(Favorite, self).save(*args, **kwargs)
        self.photo.incr('n_favorite').save()
        self.photo.user.userinfo.incr('n_favorite').save()
        return instance

    def delete(self, using=None, keep_parents=False):
        super(Favorite, self).delete(using, keep_parents)
        self.photo.incr('n_favorite', -1).save()
        self.photo.user.userinfo.incr('n_favorite', -1).save()
