from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'dj_etd.sqlite',
    }
}
################################################################################
#Update some settings for local, DB authentication (instead of Shib).
#In local_test_urls.py, it's set up to let you login through auth.views.login,
#but you'll have to manually add your user to your local database
#with "python manage.py createsuperuser".
################################################################################
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

MEDIA_URL = '/media/'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
