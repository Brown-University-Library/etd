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
      ],
     )
