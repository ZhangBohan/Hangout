import logging
from datetime import datetime

from django.conf import settings
from django.utils import timezone
from django.shortcuts import resolve_url
from wechat_sdk import WechatBasic

from hangout.models import Schedule
from wechat.models import WechatAuth


def template_notify(wechat_base: WechatBasic, wechat_auth: WechatAuth, schedule: Schedule, title: str):
    try:
        # wechat notify
        url = settings.GUPPIES_URL_PREFIX + resolve_url('hangout.detail', pk=schedule.id)

        wechat_base.send_template_message(user_id=wechat_auth.openid,
                                          template_id=settings.WECHAT_TODO_TEMPLATE_ID,
                                          url=url,
                                          data={
                                              'first': {
                                                  "value": title,
                                                  "color": "#173177"
                                              },
                                              'keyword1': {
                                                  "value": schedule.title,
                                                  "color": "#173177"
                                              },
                                              'keyword2': {
                                                  "value": schedule.started_date.strftime(
                                                      '%Y年%m月%d日 %H时%M分'),
                                                  "color": "#173177"
                                              },
                                              'remark': {
                                                  "value": schedule.content,
                                                  "color": "#173177"
                                              },
                                          })
    except Exception as e:
        logging.exception(e)


def natural_time(target_date: datetime):
    now = timezone.now()

    if now > target_date:
        delta = now - target_date
        if delta.days:
            return "%s天前" % delta.days

        if delta.seconds > 60 * 60:
            return "%s小时前" % (delta.seconds // 60 // 60)

        if delta.seconds > 60:
            return "%s分钟前" % (delta.seconds // 60)

        return "%s秒前" % delta.seconds

    delta = target_date - now

    if delta.days:
        return "%s天后" % delta.days

    if delta.seconds > 60 * 60:
        return "%s小时后" % (delta.seconds // 60 // 60)

    if delta.seconds > 60:
        return "%s分钟后" % (delta.seconds // 60)

    return "%s秒后" % delta.seconds
