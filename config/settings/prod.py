import dj_database_url

from .base import *

DATABASES = {
    'default': dj_database_url.config()
}
DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='206.189.235.97').split(',')
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://206.189.235.97',
).split(',')
STATIC_ROOT = BASE_DIR / 'staticfiles'