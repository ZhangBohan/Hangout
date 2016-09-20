from django.contrib import admin
from wechat.models import *


class PhotoAdmin(admin.ModelAdmin):
    fields = ['url', 'description', 'user', 'status']
    list_display = ('id',
                    'url',
                    'description',
                    'user',
                    'status',
                    'n_total_mark',
                    'n_account_mark',
                    'n_account_comment',
                    'n_account_vote', )

admin.site.register(WechatAuth)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(Comment)
admin.site.register(Mark)
admin.site.register(Vote)
admin.site.register(UserInfo)
