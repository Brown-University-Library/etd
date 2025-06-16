import os
from django.core.exceptions import ImproperlyConfigured
import json


def get_env_setting(setting):
    """ Get the environment setting or return exception """
    try:
        return os.environ[setting]
    except KeyError:
        error_msg = u'Set the %s env variable' % setting
        raise ImproperlyConfigured(error_msg.encode('utf8'))

CAMPUS_IPS = json.loads(get_env_setting('CAMPUS_IPS_JSON'))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DEBUG = False
SECRET_KEY = get_env_setting('SECRET_KEY')
ALLOWED_HOSTS = [get_env_setting('ALLOWED_HOST')]

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap3',
    'bulstyle',
    'crispy_forms',
    'model_utils',
    'import_export',
    'etd_app',
)

AUTHENTICATION_BACKENDS = (
    'shibboleth.backends.ShibbolethRemoteUserBackend',
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'shibboleth.middleware.ShibbolethRemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.messages.context_processors.messages',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.request',
            ]
        }
    },
]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

WSGI_APPLICATION = 'config.passenger_wsgi.application'

LANGUAGE_CODE = 'en-us'
USE_TZ = True
TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True

MEDIA_ROOT = get_env_setting('MEDIA_ROOT')
MEDIA_URL = '/etd/media/'

FILE_UPLOAD_PERMISSIONS = 0o664

STATIC_ROOT = os.path.normpath(os.path.join(BASE_DIR, 'assets'))
STATIC_URL = '/etd/static/'

LOGIN_URL = 'login'

SHIBBOLETH_ATTRIBUTE_MAP = {
   'Shibboleth-eppn': (True, 'username'),
}

LOG_DIR = get_env_setting('LOG_DIR')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'log_file':{
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR,'etd.log'),
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security.DisallowedHost': {
            'handlers': ['null'], #do nothing for disallowed hosts errors
            'propagate': False,
        },
        'etd': {
            'handlers': ['log_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}

BOOTSTRAP3 = {
    'jquery_url': '//code.jquery.com/jquery-2.2.1.min.js',
    'css_url': os.path.join(STATIC_URL,'bulstyle/css/project.css'),
}
CRISPY_TEMPLATE_PACK = 'bootstrap3'

FAST_LOOKUP_BASE_URL = 'http://fast.oclc.org/searchfast/fastsuggest'
SERVER_ROOT = get_env_setting('SERVER_ROOT')
API_URL = get_env_setting('API_URL')
GRADSCHOOL_ETD_ADDRESS = get_env_setting('GRADSCHOOL_ETD_ADDRESS')
OWNER_ID = get_env_setting('OWNER_ID')
EMBARGOED_DISPLAY_IDENTITY = get_env_setting('EMBARGOED_DISPLAY_IDENTITY')
PUBLIC_DISPLAY_IDENTITY = get_env_setting('PUBLIC_DISPLAY_IDENTITY')
POST_IDENTITY = get_env_setting('BDR_POST_IDENTITY')
AUTHORIZATION_CODE = get_env_setting('BDR_AUTHORIZATION_CODE')
EMAIL_HOST = get_env_setting('EMAIL_HOST')
SERVER_EMAIL = get_env_setting('SERVER_EMAIL')
