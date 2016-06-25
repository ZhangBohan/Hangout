from django.contrib import admin
from wechat.models import *


class PhotoAdmin(admin.ModelAdmin):
    fields = ['url', 'description', 'account_id',]

admin.site.register(Account)
admin.site.register(WechatAuth)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(Commit)
admin.site.register(Mark)
