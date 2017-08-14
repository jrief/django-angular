# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Django settings for unit test project.
import os

DEBUG = True

PROJECT_DIR = os.path.dirname(__file__)

APP_DIR = os.path.abspath(os.path.join(PROJECT_DIR, os.pardir, os.pardir))

ALLOWED_HOSTS = ['*']

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.sqlite',
    },
}

SITE_ID = 1

ROOT_URLCONF = 'server.urls'

SECRET_KEY = 'secret'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'easy_thumbnails',
    'sekizai',
    'djng',
    'server',
]

USE_L10N = True

LANGUAGE_CODE = 'en'

LANGUAGES = (
    ('en', 'English'),
    ('de', 'Deutsch'),
    ('es', 'Español'),
    ('fr', 'Français'),
    ('it', 'Italiano'),
    ('ru', 'Русский'),
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware'
)

MEDIA_ROOT = os.environ.get('DJANGO_MEDIA_ROOT', os.path.join(APP_DIR, 'workdir/media'))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory that holds static files.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.environ.get('DJANGO_STATIC_ROOT', os.path.join(APP_DIR, 'workdir/static'))

# URL that handles the static files served from STATIC_ROOT.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.environ.get('CLIENT_SRC_DIR', os.path.join(APP_DIR, 'client/src')),
    ('node_modules', os.environ.get('NODE_MODULES_DIR', os.path.join(APP_DIR, 'examples/node_modules'))),
)

FORM_RENDERER = 'djng.forms.renderers.DjangoAngularBootstrap3Templates'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'sekizai.context_processors.sekizai',
                'server.context_processors.global_context',
            ],
        },
    },
]

TIME_ZONE = 'Europe/Berlin'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[%(asctime)s %(module)s] %(levelname)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# if package django-websocket-redis is installed, some more tests can be be added
try:
    import ws4redis

    INSTALLED_APPS.append('ws4redis')

    for template in TEMPLATES:
        template['OPTIONS']['context_processors'].append('ws4redis.context_processors.default')

    # This setting is required to override the Django's main loop, when running in
    # development mode, such as ./manage runserver
    WSGI_APPLICATION = 'ws4redis.django_runserver.application'

    # URL that distinguishes websocket connections from normal requests
    WEBSOCKET_URL = '/ws/'

    # Set the number of seconds each message shall persited
    WS4REDIS_EXPIRE = 3600

    WS4REDIS_HEARTBEAT = '--heartbeat--'

    WS4REDIS_PREFIX = 'djangular'

except ImportError:
    pass
