from .base import *

import dj_database_url

DATABASES = {
    'default': dj_database_url.config()
}
DEBUG = False
ALLOWED_HOSTS = ['your-production-domain.com']