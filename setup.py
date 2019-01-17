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
          'Django>=1.11,<2.0a1',
          'django-crispy-forms==1.6.0',
          'django-model-utils==2.5',
          'django-import-export==0.5.0',
          'bdrxml @ https://github.com/Brown-University-Library/bdrxml/archive/v0.9.zip#sha1=9eeff5ed1435dac16795d54680112e15ba3bb485',
          'django-shibboleth-remoteuser @ https://github.com/Brown-University-Library/django-shibboleth-remoteuser/archive/v0.8.zip#sha1=031d66450dea0ad8ac73d0838e0d08404062ab4f',
          'django-bulstyle @ https://github.com/Brown-University-Library/django-bulstyle/archive/v1.3.zip#sha1=1986f817a2bede2a13e49e1a1b817067d9c9c04f',
          'requests==2.21.0',
      ],
     )

