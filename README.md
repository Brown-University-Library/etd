ETD application
===============

Django project for handling Electronic Theses and Dissertations.

#### Install and Run
- git clone git@github.com:Brown-University-Library/etd.git (use https://github.com/Brown-University-Library/etd.git if you're not using SSH key)
- cd etd
- [Install uv](https://docs.astral.sh/uv/getting-started/installation/) if not already installed
- set environment variables as needed
- uv sync --group test
- uv run python run\_tests.py
- uv run python manage.py migrate
- uv run python manage.py collectstatic
- uv run python manage.py runserver


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
