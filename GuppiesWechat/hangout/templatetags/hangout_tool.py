from datetime import datetime

from django import template
from django.utils import timezone

register = template.Library()


def natural_time(value: datetime):
    now = timezone.now()
    delta = now - value
    if delta > 0:
        if delta.days:
            return "%s天前" % delta.days

        if delta.seconds > 60 * 60:
            return "%s小时前" % (delta.seconds // 60 // 60)

        if delta.seconds > 60:
            return "%s分钟前" % (delta.seconds // 60)

        return "%s秒前" % delta.seconds

    delta = value - now

    if delta.days:
        return "%s天后" % delta.days

    if delta.seconds > 60 * 60:
        return "%s小时后" % (delta.seconds // 60 // 60)

    if delta.seconds > 60:
        return "%s分钟后" % (delta.seconds // 60)

    return "%s秒后" % delta.seconds


register.filter('natural_time', natural_time)
