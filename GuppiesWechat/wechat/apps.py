import functools
from django.db.models import QuerySet

from django.db import models

from django.apps import AppConfig
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse


class WechatConfig(AppConfig):
    name = 'wechat'


class WechatJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        """
        Add django model, QuerySet support
        """
        if isinstance(o, models.Model):
            data = {}
            for field in o._meta.fields:
                if hasattr(o, 'EXCLUDE_FIELDS') and field.name in o.EXCLUDE_FIELDS:
                    continue
                value = getattr(o, field.name)
                try:
                    data[field.name] = self.default(value)
                except TypeError:
                    data[field.name] = value

            if hasattr(o, 'INCLUDE_PROPERTIES'):
                for field in o.INCLUDE_PROPERTIES:
                    value = getattr(o, field)
                    try:
                        data[field] = self.default(value()) if callable(value) else value
                    except TypeError:
                        data[field] = value() if callable(value) else value
            return data
        elif isinstance(o, (list, tuple, QuerySet)):
            return [self.default(item) for item in o]
        else:
            return super(WechatJSONEncoder, self).default(o)


WechatJsonResponse = functools.partial(JsonResponse, encoder=WechatJSONEncoder, safe=False)
