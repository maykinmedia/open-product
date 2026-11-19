"""
WSGI config for openproduct project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

from django.core.wsgi import get_wsgi_application

from maykin_common.logging.wsgi import LogVars

from openproduct.setup import setup_env

setup_env()

application = LogVars(get_wsgi_application())
