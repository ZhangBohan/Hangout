import json
from urllib.parse import quote_plus

import time

import requests
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import HttpResponse, redirect, resolve_url

from django.conf import settings

from hangout.models import ScheduleShare, ScheduleUser
from hangout import logic as hangout_logic
from wechat.models import WechatAuth, UserInfo, UserLocation
from wechat.utils import upload_url_to_qiniu
import logging


def callback(request):
    signature = request.GET.get('signature')
    timestamp = request.GET.get('timestamp')
    nonce = request.GET.get('nonce')
    echostr = request.GET.get('echostr')

    wechat_base = settings.WECHAT_BASIC

    print('初始化:', request.GET, settings.WECHAT_CONF.appid, signature, timestamp, nonce, echostr)
    print('body:', request.body.decode())

    if not wechat_base.check_signature(request.GET.get('signature'),
                                       request.GET.get('timestamp'),
                                       request.GET.get('nonce')):
        print('验证不通过!')
        raise Http404()

    from wechat_sdk.exceptions import ParseError
    try:
        wechat_base.parse_data(request.body)
    except ParseError:
        print('Invalid Body Text')
        raise Http404()

    print('wechat_base.message:', wechat_base.message, wechat_base.message.type)

    if wechat_base.message.type in ['scan', 'subscribe']:
        key = wechat_base.message.key
        source = wechat_base.message.source
        print('关注事件', key, source)
        wechat_auth = _get_wechat_auth(wechat_base, openid=source)
        if not key:
            text = wechat_base.response_text('关注成功!')
            print('return by empty key', text)
            return HttpResponse(text)

        prefix = 'qrscene_'
        key = key.replace(prefix, '')

        # 已关注用户扫二维码
        print('auth', wechat_auth, wechat_auth.user)
        try:
            schedule_share = _accept_schedule(ss_id=int(key), user=wechat_auth.user)
        except (ValueError, ScheduleShare.DoesNotExist) as e:
            logging.exception(e)
            return HttpResponse(wechat_base.response_text('该邀请不存在!ID: %s' % key))

        print("发送模板消息。。。。。。。。。")
        schedule = schedule_share.schedule

        if schedule.user_id == wechat_auth.user_id:
            text = '该事件是您创建的, 您无需扫码加入!'
        else:
            text = '恭喜你预约成功, 我将于%s提醒您!' % (hangout_logic.natural_time(schedule.started_date))

        hangout_logic.template_notify(wechat_auth, schedule, title=text)
    return HttpResponse("")


def _accept_schedule(ss_id, user):
    schedule_share = ScheduleShare.objects.get(pk=ss_id)

    if not schedule_share.schedule.user_id == user.id:
        su, created = ScheduleUser.objects.get_or_create(schedule=schedule_share.schedule, user=user)
        if created:
            su.save()

    return schedule_share


def _get_wechat_auth(wechat_base, openid):
    access_token = wechat_base.get_access_token().get('access_token')
    try:
        wechat_auth = WechatAuth.objects.get(openid=openid)
    except WechatAuth.DoesNotExist:
        wechat_user_dict = wechat_base.get_user_info(openid)
        data = {}
        # FIXME unionid is empty。只有在用户将公众号绑定到微信开放平台帐号后，才会出现该字段
        for key in ['openid', 'nickname', 'sex', 'city', 'province', 'language', 'headimgurl']:
            data[key] = wechat_user_dict[key]

        wechat_auth = WechatAuth.objects.create(access_token=access_token,
                                                refresh_token=access_token,
                                                expires_in=-1,
                                                **data)

    user = wechat_auth.user

    if not user:
        username = 'wechat_{auth_id}'.format(auth_id=wechat_auth.id)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(username=username,
                                            password=wechat_auth.openid)
            user.save()

        wechat_auth.user = user
        wechat_auth.save()

    if wechat_auth.headimgurl:
        key = '{user_id}_avatar_{timestamp}'.format(user_id=user.id, timestamp=time.time())
        url = upload_url_to_qiniu(key, wechat_auth.headimgurl)
    else:
        # FIXME default avatar
        url = 'http://bohan.qiniudn.com/2016-07-20_github.png'

    UserInfo.objects.get_or_create(user=user,
                                   defaults={
                                       'nickname': wechat_auth.nickname,
                                       'avatar_url': url
                                   }
                                   )

    return wechat_auth


def auth(request):
    if 'account' in request.session:
        return HttpResponse("ok")

    code = request.GET.get('code')
    if not code:
        encoded_url = quote_plus(request.build_absolute_uri(reverse('auth')))
        url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&' \
              'scope=%s&state=%s#wechat_redirect' % (
                  settings.WECHAT_CONF.appid, encoded_url, 'snsapi_userinfo', None)
        return redirect(url)

    params = {
        "appid": settings.WECHAT_CONF.appid,
        "secret": settings.WECHAT_CONF.appsecret,
        "code": code,
        "grant_type": 'authorization_code'
    }

    response = requests.get('https://api.weixin.qq.com/sns/oauth2/access_token', params=params)
    logging.info('response:', response.content)
    print('response:', response.content)
    if response.status_code != 200:
        logging.error('wechat auth error. status code: %s' % response.status_code)
        return HttpResponse(response.content, status=500)

    data = response.json()

    if data.get('errcode'):  # invalid code
        return HttpResponse(response.content, status=500)

    access_token = data.get('access_token')
    refresh_token = data.get('refresh_token')
    expires_in = data.get('expires_in')
    openid = data.get('openid')
    unionid = data.get('unionid')

    rv = requests.get('https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN' % (
        access_token, openid))

    content = rv.content.decode('utf-8')
    user_data = json.loads(content)
    user_data.pop('privilege')
    created = False
    if unionid:
        wechat_auth = WechatAuth.objects.get(unionid=unionid)
        if wechat_auth:
            wechat_auth, created = WechatAuth.objects.update_or_create(unionid=unionid,
                                                                       expires_in=expires_in,
                                                                       defaults=dict(access_token=access_token,
                                                                                     refresh_token=refresh_token,
                                                                                     **user_data))
    if not created:
        wechat_auth, created = WechatAuth.objects.update_or_create(openid=openid,
                                                                   expires_in=expires_in,
                                                                   defaults=dict(access_token=access_token,
                                                                                 refresh_token=refresh_token,
                                                                                 **user_data))

    try:
        user = User.objects.get(username='wechat_{auth_id}'.format(auth_id=wechat_auth.id))
    except User.DoesNotExist:
        user = User.objects.create_user(username='wechat_{auth_id}'.format(auth_id=wechat_auth.id),
                                        password=wechat_auth.openid)
        user.save()

    key = '{user_id}_avatar_{timestamp}'.format(user_id=user.id, timestamp=time.time())
    try:
        UserInfo.objects.get(user=user)
    except UserInfo.DoesNotExist:
        if wechat_auth.headimgurl:
            url = upload_url_to_qiniu(key, wechat_auth.headimgurl)
        else:
            # FIXME default avatar
            url = 'http://bohan.qiniudn.com/2016-07-20_github.png'
        UserInfo.objects.create(user=user,
                                nickname=wechat_auth.nickname,
                                avatar_url=url
                                ).save()

    try:
        UserLocation.objects.get(user=user)
    except UserLocation.DoesNotExist:
        UserLocation.objects.create(user=user,
                                    province=wechat_auth.province,
                                    city=wechat_auth.city,
                                    ).save()

    auth_user = authenticate(username=user.username, password=wechat_auth.openid)
    if auth_user is not None:
        # the password verified for the user
        if auth_user.is_active:
            login(request, auth_user)
            return redirect('hangout.index')
        else:
            return HttpResponse("The password is valid, but the account has been disabled!")
    return HttpResponse("user or password error", status=500)
