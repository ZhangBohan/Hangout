from django.shortcuts import render, HttpResponse
from wechat_sdk import WechatConf, WechatBasic

conf = WechatConf(
    token='98671d2d-fb6b-49e1-920a-7ae2d034011',
    appid='wxbbb6b25e8943502f',
    appsecret='8140ce54ce5c261fcf1a56fa3e3cc9ca',
    encrypt_mode='safe',  # 可选项：normal/compatible/safe，分别对应于 明文/兼容/安全 模式
    # encoding_aes_key='your_encoding_aes_key'  # 如果传入此值则必须保证同时传入 token, appid
)

wechat_basic = WechatBasic(conf=conf)


def index(request):
    return HttpResponse("Hello, world. You're at the wechat index.")


def callback(request):
    print(request.GET)
    if wechat_basic.check_signature(request.GET.get('signature'),
                                    request.GET.get('timestamp'),
                                    request.GET.get('nonce')):
        return HttpResponse("ok")
    else:
        return HttpResponse("error", status=500)
