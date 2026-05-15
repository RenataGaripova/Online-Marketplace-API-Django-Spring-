# Project modules
from decouple import config
from settings.base import *



DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB', default='marketplace'),
        'USER': config('POSTGRES_USER', default='marketplace'),
        'PASSWORD': config('POSTGRES_PASSWORD', default='marketplace'),
        'HOST': config('POSTGRES_HOST', default='db'),
        'PORT': config('POSTGRES_PORT', default='5432'),
    }
}
