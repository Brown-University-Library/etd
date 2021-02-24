#!/usr/bin/env python
from os.path import dirname, abspath, join
import sys
import dotenv

if __name__ == "__main__":
    SITE_ROOT = dirname(abspath(__file__))
    if SITE_ROOT not in sys.path:
        sys.path.append(SITE_ROOT)

    PROJECT_ROOT = dirname(SITE_ROOT)
    dotenv.read_dotenv(join(PROJECT_ROOT, '.env'))

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
