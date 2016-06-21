from django.db import models


class Account(models.Model):
    nickname = models.CharField("昵称", max_length=100)
    avatar_url = models.URLField("头像")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class WechatAuth(models.Model):
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

    account_id = models.ForeignKey("Account", null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
