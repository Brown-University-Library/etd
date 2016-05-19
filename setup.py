from __future__ import unicode_literals
from setuptools import setup

setup(name='bdr-etd-app',
      version='0.5',
      description='App for storing and working with dissertations',
      author='Brown University Libraries',
      author_email='bdr@brown.edu',
      url='https://github.com/Brown-University-Library/etd_app',
      packages=[str('etd_app')], # https://bugs.python.org/issue13943
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Django>=1.8,<1.9',
          'django-crispy-forms==1.6.0',
          'bdrxml==0.8a1',
          'django-shibboleth-remoteuser==0.7',
          'django-bulstyle==1.0.0',
          'pytz==2016.4',
          'requests',
      ],
      dependency_links=[
          'https://github.com/Brown-University-Library/bdrxml/archive/master.zip',
          'https://github.com/Brown-University-Library/django-shibboleth-remoteuser/archive/v0.7.zip',
          'https://github.com/Brown-University-Library/django-bulstyle/archive/master.zip',
      ],
     )
