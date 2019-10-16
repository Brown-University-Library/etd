from setuptools import setup

setup(name='bdr-etd-app',
      version='0.5',
      description='App for storing and working with dissertations',
      author='Brown University Libraries',
      author_email='bdr@brown.edu',
      url='https://github.com/Brown-University-Library/etd_app',
      packages=['etd_app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Django~=1.11',
          'django-crispy-forms',
          'django-model-utils',
          'django-import-export',
          'bdrxml',
          'django-shibboleth-remoteuser',
          'django-bulstyle @ https://github.com/Brown-University-Library/django-bulstyle/archive/v1.3.zip#sha1=1986f817a2bede2a13e49e1a1b817067d9c9c04f',
          'requests',
      ],
      extras_require={
        'dev':  ['responses'],
    }
     )

