from django.contrib import admin
from wechat.models import Account, WechatAuth

admin.site.register(Account)
admin.site.register(WechatAuth)
