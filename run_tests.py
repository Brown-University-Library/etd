#!/usr/bin/env python
from __future__ import unicode_literals
import os
import shutil
import sys
import tempfile
import django
from django.conf import settings
from django.test.utils import get_runner


if __name__ == '__main__':
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
    tmp_media_root = tempfile.mkdtemp(prefix='etd_testsuite_tmp') #TODO: use context manager in python3
    shutil.copytree('tests/test_files', '%s/test_files' % tmp_media_root)
    django.setup()
    settings.MEDIA_ROOT = tmp_media_root
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['tests'])
    shutil.rmtree(tmp_media_root)
    sys.exit(bool(failures))

