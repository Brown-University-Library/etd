#!/usr/bin/env python
import os
import sys
import tempfile
import django
from django.conf import settings
from django.test.utils import get_runner


if __name__ == '__main__':
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.unit_tests'
    os.environ['SECRET_KEY'] = '1234567890'
    os.environ['GRADSCHOOL_ETD_ADDRESS'] = 'random@example.org'
    os.environ['OWNER_ID'] = 'OWNER_ID'
    os.environ['EMBARGOED_DISPLAY_IDENTITY'] = 'EMBARGO'
    os.environ['PUBLIC_DISPLAY_IDENTITY'] = 'PUBLIC'
    os.environ['BDR_POST_IDENTITY'] = 'BDR_POST_IDENTITY'
    os.environ['BDR_AUTHORIZATION_CODE'] = 'BDR_AUTHORIZATION_CODE'
    os.environ['EMAIL_HOST'] = 'EMAIL_HOST'
    os.environ['SERVER_EMAIL'] = 'SERVER_EMAIL'
    os.environ['SERVER_ROOT'] = 'http://localhost/'
    os.environ['API_URL'] = 'http://localhost/api/'
    os.environ['ALLOWED_HOST'] = 'localhost'
    os.environ['CAMPUS_IPS_JSON'] = '["10.0.0.0/8", "128.148.0.0/16", "138.16.0.0/16"]'
    with tempfile.TemporaryDirectory() as tmp:
        os.environ['MEDIA_ROOT'] = os.path.join(tmp, 'media')
        os.environ['LOG_DIR'] = tmp
        django.setup()
        TestRunner = get_runner(settings)
        test_runner = TestRunner()
        failures = test_runner.run_tests(['tests'])
    sys.exit(bool(failures))
