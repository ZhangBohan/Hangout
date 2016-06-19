from django.contrib import admin
from wechat.models import Account, Session, WechatAuth

admin.site.register(Account)
admin.site.register(Session)
admin.site.register(WechatAuth)
