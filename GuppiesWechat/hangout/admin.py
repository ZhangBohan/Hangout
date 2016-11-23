from django.contrib import admin

from hangout.models import *

admin.register(Template)
admin.register(Schedule)
admin.register(ScheduleUser)
admin.register(ScheduleShare)
admin.register(HangoutConfig)
