import io

import requests
from rest_framework import pagination
from rest_framework.response import Response

from qiniu import Auth, put_data

access_key = '1H3USr1wF7hQ80AeRlq_BF0KoEnoJq2atE4UULwp'
secret_key = 'awFedibl6FB3L-4FSXG1NY4Qq3MFwiDoZcNFDKTF'

q = Auth(access_key, secret_key)
bucket_name = 'guppies'
base_url = 'http://oa3rslghz.bkt.clouddn.com/'


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
