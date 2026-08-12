from .base import *

DEBUG = True

TEMPLATES[0]['DIRS'] = [os.path.join(BASE_DIR, 'tests', 'templates')] + TEMPLATES[0]['DIRS']

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
