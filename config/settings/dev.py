from .base import *
import dj_database_url
from decouple import config

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': dj_database_url.config(default=config('DATABASE_URL'))
}