"""
WSGI config for openproduct project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

from datetime import datetime, timezone

from django.core.wsgi import get_wsgi_application

from openproduct.setup import setup_env

try:
    import uwsgi  # pyright: ignore[reportMissingModuleSource] uwsgi magic...
except ImportError:
    uwsgi = None

setup_env()


class LogVars:
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        if uwsgi is not None:
            now = datetime.now(tz=timezone.utc)
            uwsgi.set_logvar("iso8601timestamp", now.isoformat())
        return self.application(environ, start_response)


application = LogVars(get_wsgi_application())
