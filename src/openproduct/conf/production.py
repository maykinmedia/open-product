"""
Production environment settings module.
Tweaks the base settings so that caching mechanisms are used where possible,
and HTTPS is leveraged where possible to further secure things.
"""

import os

os.environ.setdefault("ENVIRONMENT", "production")
# NOTE: watch out for multiple projects using the same cache!
os.environ.setdefault("CACHE_DEFAULT", "127.0.0.1:6379/2")

from .base import *  # noqa isort:skip

# Make use of persistent connections for better database performance
# If not specified database connections are closed at the end of each request
for db_config in DATABASES.values():
    db_config["CONN_MAX_AGE"] = config(
        "DB_CONN_MAX_AGE", default=0
    )  # Lifetime of a database connection in seconds

# Caching sessions.
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Caching templates.
TEMPLATES[0]["OPTIONS"]["loaders"] = [
    ("django.template.loaders.cached.Loader", TEMPLATE_LOADERS)
]

# The file storage engine to use when collecting static files with the
# collectstatic management command.
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

# Production logging facility.

# Production logging facility.
LOGGING["loggers"].update(
    {
        "django": {
            "handlers": logging_root_handlers,
            "level": "INFO",
            "propagate": False,
        },
        "django.security.DisallowedHost": {
            "handlers": logging_root_handlers,
            "level": "CRITICAL",
            "propagate": False,
        },
    }
)

# Only set this when we're behind a reverse proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_CONTENT_TYPE_NOSNIFF = True  # Sets X-Content-Type-Options: nosniff
SECURE_BROWSER_XSS_FILTER = True  # Sets X-XSS-Protection: 1; mode=block

##############################
#                            #
# 3RD PARTY LIBRARY SETTINGS #
#                            #
##############################

# APM
MIDDLEWARE = ["elasticapm.contrib.django.middleware.TracingMiddleware"] + MIDDLEWARE
INSTALLED_APPS = INSTALLED_APPS + [
    "elasticapm.contrib.django",
]

if SUBPATH and SUBPATH != "/":
    STATIC_URL = f"{SUBPATH}{STATIC_URL}"
    MEDIA_URL = f"{SUBPATH}{MEDIA_URL}"
