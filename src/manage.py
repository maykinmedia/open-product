#!/usr/bin/env python
import sys

from openproduct.setup import setup_env

if __name__ == "__main__":
    setup_env()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as e:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from e
    execute_from_command_line(sys.argv)
