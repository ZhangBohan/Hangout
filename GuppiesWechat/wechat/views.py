from django.shortcuts import render
from wechat_sdk import WechatConf

conf = WechatConf(
    token='98671d2d-fb6b-49e1-920a-7ae2d034011',
    appid='wxbb6d9fadb822c1f4',
    appsecret='3b2ef12344a9aef5c2d4fa991076e9f7',
    encrypt_mode='safe',  # 可选项：normal/compatible/safe，分别对应于 明文/兼容/安全 模式
    encoding_aes_key='your_encoding_aes_key'  # 如果传入此值则必须保证同时传入 token, appid
)
