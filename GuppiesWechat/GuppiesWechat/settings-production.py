import raven
from .settings import *

DEBUG = False

RAVEN_CONFIG = {
    'dsn': 'https://0295646ba4bd4f71bfed6f401833c67a:bf0f6796a3df41d28680e4a903ae7416@sentry.io/82095',
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': raven.fetch_git_sha(os.path.dirname(BASE_DIR)),
}


WECHAT_CONF = WechatConf(
    token='guppiestoken',
    appid='wxbc67178dd545c3db',
    appsecret='8140ce54ce5c261fcf1a56fa3e3cc9ca',
    encrypt_mode='normal',  # 可选项：normal/compatible/safe，分别对应于 明文/兼容/安全 模式
    # encoding_aes_key='your_encoding_aes_key'  # 如果传入此值则必须保证同时传入 token, appid
)

WECHAT_BASIC = WechatBasic(conf=WECHAT_CONF)

WECHAT_NOTIFY_TEMPLATE_ID = 'J-aNQpG-wovUB3qxBnQ-iLNH5TrCHO4x4er3NTRYIxQ'
WECHAT_TODO_TEMPLATE_ID = 'AswFc63iemsfyrcj1YH6DPkA6GNjBFLE6EnQ6XE8D3Q'
