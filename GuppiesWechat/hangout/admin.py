from django.contrib import admin

from hangout.models import *


class ScheduleAdmin(admin.ModelAdmin):
    fields = ['title', 'content', 'user', 'is_notified', 'started_date', 'ended_date']
    list_display = ('id',
                    'title',
                    'user',
                    'is_notified',
                    'started_date',
                    'notify_other',
                    'accepted_count',)

admin.site.register(Template)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(ScheduleUser)
admin.site.register(ScheduleShare)
admin.site.register(HangoutConfig)
