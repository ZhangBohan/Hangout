import raven
from .settings import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'db',
        'PORT': '5432',
    }
}

RAVEN_CONFIG = {
    'dsn': 'https://0295646ba4bd4f71bfed6f401833c67a:bf0f6796a3df41d28680e4a903ae7416@sentry.io/82095',
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': raven.fetch_git_sha(os.path.dirname(BASE_DIR)),
}

WECHAT_APPID = 'wxbc67178dd545c3db'
WECHAT_APPSECRET = 'f6fb6117b6d1daaa95804b083eef09a7'
WECHAT_NOTIFY_TEMPLATE_ID = 'AvRdqkq7symye0wnu6S_7IpjbuZwsOv_1FKKZE0mi44'
WECHAT_TODO_TEMPLATE_ID = 'DIM9HipuD3plhVbQi_VLpw0rbMRDNfi_PrwTUNxgWDI'

GUPPIES_URL_PREFIX = 'http://woaixiaoyu.com'
