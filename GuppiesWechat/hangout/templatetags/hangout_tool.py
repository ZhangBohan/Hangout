from datetime import datetime

from django import template
from hangout import logic as hangout_logic

register = template.Library()


def natural_time(value: datetime):
    return hangout_logic.natural_time(value)


register.filter('natural_time', natural_time)
