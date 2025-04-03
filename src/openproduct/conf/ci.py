import os

os.environ.setdefault("DEBUG", "no")
os.environ.setdefault("ENVIRONMENT", "ci")
os.environ.setdefault("SECRET_KEY", "for-testing-purposes-only")
os.environ.setdefault("IS_HTTPS", "no")
os.environ.setdefault("ALLOWED_HOSTS", "")

from .base import *  # noqa isort:skip

LOGGING["loggers"].update(
    {
        "django": {
            "handlers": ["django"],
            "level": "WARNING",
            "propagate": True,
        },
    }
)

CACHES.update(
    {
        "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
        # See: https://github.com/jazzband/django-axes/blob/master/docs/configuration.rst#cache-problems
        "axes": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"},
        "oidc": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    }
)

# Django solo caching (disabled for CI)
SOLO_CACHE = None

#
# Django-axes
#
AXES_BEHIND_REVERSE_PROXY = False

# THOU SHALT NOT USE NAIVE DATETIMES
warnings.filterwarnings(
    "error",
    r"DateTimeField .* received a naive datetime",
    RuntimeWarning,
    r"django\.db\.models\.fields",
)

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
