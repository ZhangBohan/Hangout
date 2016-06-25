from django.contrib import admin
from wechat.models import *


class PhotoAdmin(admin.ModelAdmin):
    fields = ['url', 'description', 'account']
    list_display = ('url',
                    'description',
                    'account',
                    'n_total_mark',
                    'n_account_mark',
                    'n_account_commit',
                    'n_account_vote', )

admin.site.register(Account)
admin.site.register(WechatAuth)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(Commit)
admin.site.register(Mark)
