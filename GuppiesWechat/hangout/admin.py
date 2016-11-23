from django.contrib import admin

from hangout.models import *

admin.site.register(Template)
admin.site.register(Schedule)
admin.site.register(ScheduleUser)
admin.site.register(ScheduleShare)
admin.site.register(HangoutConfig)
