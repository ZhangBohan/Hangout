import io

import requests
from rest_framework import pagination
from rest_framework.response import Response

from qiniu import Auth, put_stream

access_key = '1H3USr1wF7hQ80AeRlq_BF0KoEnoJq2atE4UULwp'
secret_key = 'awFedibl6FB3L-4FSXG1NY4Qq3MFwiDoZcNFDKTF'

q = Auth(access_key, secret_key)
bucket_name = 'guppies'
base_url = 'http://oa3rslghz.bkt.clouddn.com/'


def upload_url_to_qiniu(key, url):
    r = requests.get(url)

    return upload_stream_to_qiniu(key, io.BytesIO(r.content))


def upload_stream_to_qiniu(key, stream):
    token = q.upload_token(bucket_name, key, 3600)

    ret, info = put_stream(token, key, stream, file_name=key, data_size=len(stream))
    print(info)
    return "{base_url}{key}".format(base_url=base_url, key=key)


class CustomPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'page': self.page.number,
            'size': self.page_size,
            'has_next': self.page.paginator.num_pages > self.page.number,
            'count': self.page.paginator.count,
            'results': data
        })
