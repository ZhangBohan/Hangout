from datetime import datetime

from django.core.management.base import BaseCommand

from hangout.models import Schedule


class Command(BaseCommand):
    def handle(self, *args, **options):
        now = datetime.now()
        for schedule in Schedule.objects.filter(started_date__lt=now, is_notified=False).all():

            # FIXME wechat notify
            schedule.after_notify()
