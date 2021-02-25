ETD application
===============

Django project for handling Electronic Theses and Dissertations.

#### Install and Run
- mkdir etd\_project
- cd etd\_project
- python3 -m venv env
- set environment variables in env/bin/activate
- source env/bin/activate
- python3 -m pip install --upgrade pip
- git clone git@github.com:Brown-University-Library/etd.git (use https://github.com/Brown-University-Library/etd.git if you're not using SSH key)
- cd etd
- pip install -r requirements/dev.txt
- python run\_tests.py
- python manage.py migrate
- python manage.py collectstatic
- python manage.py runserver


License
=======

[ETD app] [EA] by [Brown University Library] [BUL]
is licensed under a [Creative Commons Attribution-ShareAlike 3.0 Unported License] [CC BY-SA 3.0]

[EA]: https://github.com/Brown-University-Library/etd_app
[BUL]: http://library.brown.edu/its/software/
[CC BY-SA 3.0]: http://creativecommons.org/licenses/by-sa/3.0/

Human readable summary:

    You are free:
    - to Share — to copy, distribute and transmit the work
    - to Remix — to adapt the work
    - to make commercial use of the work

    Under the following conditions:
    - Attribution — You must attribute the work to:
      Brown University Library - http://library.brown.edu/its/software/
    - Share Alike — If you alter, transform, or build upon this work,
      you may distribute the resulting work only under the same
      or similar license to this one.

---
