import io
import logging

import requests
from rest_framework import fields
from rest_framework import pagination
from rest_framework import serializers
from rest_framework.response import Response

from qiniu import Auth, put_data

access_key = '1H3USr1wF7hQ80AeRlq_BF0KoEnoJq2atE4UULwp'
secret_key = 'awFedibl6FB3L-4FSXG1NY4Qq3MFwiDoZcNFDKTF'

q = Auth(access_key, secret_key)
bucket_name = 'guppies'
base_url = 'http://oa3rslghz.bkt.clouddn.com/'


def gaode_location(latitude, longitude):
    url = 'http://restapi.amap.com/v3/geocode/regeo'

    params = {
        'location': '%s,%s' % (longitude, latitude),
        'key': 'c55ecd2ce9d9e5c64c6f5ea13ccdbe43'
    }

    r = requests.get(url, params=params)
    result = r.json()
    if result.get('infocode') != '10000':
        logging.error(r.content)
        print(r.content)
        raise Exception()

    print('location', latitude, longitude, result)
    addressComponent = result['regeocode']['addressComponent']
    province = addressComponent['province']
    city = addressComponent['city'] if addressComponent['city'] else province
    district = addressComponent['district']
    return province, city, district



def upload_url_to_qiniu(key, url):
    r = requests.get(url)

    return upload_stream_to_qiniu(key, r.content)


def upload_stream_to_qiniu(key, data):
    token = q.upload_token(bucket_name, key, 3600)

    ret, info = put_data(token, key, data)
    print(info)
    return "{base_url}{key}".format(base_url=base_url, key=key)


class CustomPagination(pagination.PageNumberPagination):
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'page': self.page.number,
            'page_size': self.page_size,
            'has_next': self.page.paginator.num_pages > self.page.number,
            'count': self.page.paginator.count,
            'results': data
        })


class JsonPropertyField(serializers.Field):
    output_func_name = 'output_func'

    def __init__(self, **kwargs):
        if self.output_func_name in kwargs:
            setattr(self, self.output_func_name, kwargs.pop(self.output_func_name))
        super(JsonPropertyField, self).__init__(**kwargs)

    def get_attribute(self, instance):
        """
        Given the *outgoing* object instance, return the primitive value
        that should be used for this field.
        """
        try:
            return fields.get_attribute(instance, self.source_attrs)
        except (KeyError, AttributeError) as exc:
            return None if self.default == fields.empty else self.default

    def to_representation(self, value):
        return getattr(self, self.output_func_name)(value) if hasattr(self, self.output_func_name) else value

    def to_internal_value(self, data):
        return data
