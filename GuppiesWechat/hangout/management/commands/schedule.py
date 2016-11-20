from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from hangout.models import Schedule


class Command(BaseCommand):
    def handle(self, *args, **options):
        pass
