import json
from urllib.parse import quote_plus

import time

import requests
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from wechat.models import WechatAuth, UserInfo, Photo, Comment, Vote, UserLocation
from wechat.utils import upload_url_to_qiniu
from wechat_sdk import WechatConf, WechatBasic
import logging

conf = WechatConf(
    token='guppiestoken',
    appid='wxbbb6b25e8943502f',
    appsecret='8140ce54ce5c261fcf1a56fa3e3cc9ca',
    encrypt_mode='normal',  # 可选项：normal/compatible/safe，分别对应于 明文/兼容/安全 模式
    # encoding_aes_key='your_encoding_aes_key'  # 如果传入此值则必须保证同时传入 token, appid
)

wechat_basic = WechatBasic(conf=conf)


@login_required
def photo_index(request):
    photos = Photo.objects.all()
    return render(request, 'wechat_photo_index.html', context={
        "photos": photos
    })


@login_required
def photo_detail(request, pk):
    photo = Photo.objects.get(pk=pk)
    photo.incr('n_total_watched').save()

    comments = Comment.objects.filter(photo=photo)
    votes = Vote.objects.filter(photo=photo)[:5]
    return render(request, 'wechat_photo_detail.html', context={
        "photo": photo,
        "comments": comments,
        "votes": votes,
    })


@login_required
def vote_index(request, photo_id):
    votes = Vote.objects.filter(photo_id=photo_id)
    return render(request, 'wechat_vote_index.html', context={
        "votes": votes
    })


@login_required
def mine(request):
    return render(request, 'wechat_mine.html', context={
        "user": request.user
    })


@login_required
def rank_index(request):
    return render(request, 'wechat_rank_index.html', context={
        "user": request.user
    })


@login_required
def rank_scores(request):
    photos = Photo.objects.all()
    return render(request, 'wechat_rank_scores.html', context={
        "user": request.user,
        "photos": photos
    })


@login_required
def rank_users(request):
    userinfos = UserInfo.objects.all()
    return render(request, 'wechat_rank_users.html', context={
        "user": request.user,
        "userinfos": userinfos
    })


def callback(request):
    signature = request.GET.get('signature')
    timestamp = request.GET.get('timestamp')
    nonce = request.GET.get('nonce')
    echostr = request.GET.get('echostr')

    print(request.GET, conf.appid, signature, timestamp, nonce, echostr)

    if wechat_basic.check_signature(request.GET.get('signature'),
                                    request.GET.get('timestamp'),
                                    request.GET.get('nonce')):
        return HttpResponse(echostr)
    else:

        return HttpResponse(wechat_basic.response_text('工程师正在努力开发中'))


def auth(request):
    if 'account' in request.session:
        return HttpResponse("ok")

    code = request.GET.get('code')
    if not code:
        encoded_url = quote_plus(request.build_absolute_uri(reverse('auth')))
        url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&' \
              'scope=%s&state=%s#wechat_redirect' % (
                  conf.appid, encoded_url, 'snsapi_userinfo', None)
        return redirect(url)

    params = {
        "appid": conf.appid,
        "secret": conf.appsecret,
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
        url = upload_url_to_qiniu(key, wechat_auth.headimgurl)
        UserInfo.objects.create(user=user,
                                nickname=wechat_auth.nickname,
                                avatar_url=url
                                ).save()

    try:
        UserLocation.objects.get(user=user)
    except UserLocation.DoesNotExist:
        UserLocation.objects.create(user=user,
                                    country=wechat_auth.country,
                                    province=wechat_auth.province,
                                    city=wechat_auth.city,
                                    ).save()

    auth_user = authenticate(username=user.username, password=wechat_auth.openid)
    if auth_user is not None:
        # the password verified for the user
        if auth_user.is_active:
            login(request, auth_user)
            return redirect('photo-index')
        else:
            return HttpResponse("The password is valid, but the account has been disabled!")
    return HttpResponse("user or password error", status=500)
