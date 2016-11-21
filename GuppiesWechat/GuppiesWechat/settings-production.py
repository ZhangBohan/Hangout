import raven
from .settings import *

DEBUG = True

RAVEN_CONFIG = {
    'dsn': 'https://0295646ba4bd4f71bfed6f401833c67a:bf0f6796a3df41d28680e4a903ae7416@sentry.io/82095',
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': raven.fetch_git_sha(os.path.dirname(BASE_DIR)),
}

WECHAT_NOTIFY_TEMPLATE_ID = 'J-aNQpG-wovUB3qxBnQ-iLNH5TrCHO4x4er3NTRYIxQ'
WECHAT_TODO_TEMPLATE_ID = 'AswFc63iemsfyrcj1YH6DPkA6GNjBFLE6EnQ6XE8D3Q'
