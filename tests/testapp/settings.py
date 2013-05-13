# Django settings for unit test project.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.sqlite',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
}

SITE_ID = 1

ROOT_URLCONF = 'testapp.urls'

SECRET_KEY = 'SSponU8sDrOMjaSCjmQ0D04PlrLugv3vJDjzEipb'

STATIC_URL = '/static/'

INSTALLED_APPS = (
#    'django.contrib.auth',
#    'django.contrib.contenttypes',
#    'django.contrib.sessions',
#    'django.contrib.sites',
#    'django.contrib.messages',
    'djangular',
)
