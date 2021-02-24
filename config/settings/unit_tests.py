from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'USER': '',
        'PASSWORD': '',
	'HOST': '',
        'PORT': '',
    }
}

#raise exception on template errors
TEMPLATES[0]['OPTIONS']['debug'] = True
