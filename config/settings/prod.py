import dj_database_url

from .base import *

DATABASES = {
    'default': dj_database_url.config()
}
DEBUG = False
ALLOWED_HOSTS = ['your-production-domain.com']