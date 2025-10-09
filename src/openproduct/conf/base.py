import os

from django.utils.translation import gettext_lazy as _

from celery.schedules import crontab

os.environ["_USE_STRUCTLOG"] = "True"

from open_api_framework.conf.base import *  # noqa: F403
from open_api_framework.conf.utils import config

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = "nl"

TIME_ZONE = "Europe/Amsterdam"  # note: this *may* affect the output of DRF datetimes

INSTALLED_APPS += [
    # 'django.contrib.admindocs',
    # 'django.contrib.humanize',
    # 'django.contrib.sitemaps',
    # External applications.
    # Project applications.
    "rest_framework.authtoken",
    "timeline_logger",
    "parler",
    "django_celery_beat",
    "reversion",
    "reversion_compare",
    "openproduct.accounts",
    "openproduct.logging",
    "openproduct.utils",
    "openproduct.producttypen",
    "openproduct.producten",
    "openproduct.locaties",
    "openproduct.urn",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", PROJECT_DIRNAME),
        "USER": config("DB_USER", PROJECT_DIRNAME),
        "PASSWORD": config("DB_PASSWORD", PROJECT_DIRNAME),
        "HOST": config("DB_HOST", "localhost"),
        "PORT": config("DB_PORT", 5432),
    }
}

MIDDLEWARE.insert(
    MIDDLEWARE.index("django.middleware.common.CommonMiddleware"),
    "openproduct.utils.middleware.APILocaleMiddleware",
)

MIDDLEWARE += [
    "reversion.middleware.RevisionMiddleware",
    "openproduct.utils.middleware.APIVersionHeaderMiddleware",
]

#
# MOZILLA DJANGO OIDC
#

OIDC_DRF_AUTH_BACKEND = "openproduct.utils.oidc_backend.OIDCAuthenticationBackend"

OIDC_CREATE_USER = config(
    "OIDC_CREATE_USER",
    default=True,
    help_text="whether the OIDC authorization will create users if the user is unknown in Open Product.",
)

#
# CELERY
#

# amount of days to keep when the 'Prune timeline logs' task is called.
PRUNE_LOGS_TASK_KEEP_DAYS = 30

CELERY_BROKER_URL = "redis://localhost:6379"  # Redis broker
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_BEAT_SCHEDULE = {
    "Update product statussen": {
        "task": "openproduct.producten.tasks.set_product_states",
        "schedule": crontab(minute="0", hour="0"),
    },
    "Prune timeline logs": {
        "task": "openproduct.logging.tasks.prune_logs",
        "schedule": crontab(minute="0", hour="0", day_of_month="1"),
        "args": (PRUNE_LOGS_TASK_KEEP_DAYS,),
    },
}

#
# Custom settings
#
SITE_TITLE = "API dashboard"
PROJECT_NAME = "Open Product"
SHOW_ALERT = True

# This setting is used by the csrf_failure view (accounts app).
# You can specify any path that should match the request.path
# Note: the LOGIN_URL Django setting is not used because you could have
# multiple login urls defined.
LOGIN_URLS = [reverse_lazy("admin:login")]

# Default (connection timeout, read timeout) for the requests library (in seconds)
REQUESTS_DEFAULT_TIMEOUT = (10, 30)

##############################
#                            #
# 3RD PARTY LIBRARY SETTINGS #
#                            #
##############################

#
# Django setup configuration
#
SETUP_CONFIGURATION_STEPS = (
    "zgw_consumers.contrib.setup_configuration.steps.ServiceConfigurationStep",
    "notifications_api_common.contrib.setup_configuration.steps.NotificationConfigurationStep",
    "mozilla_django_oidc_db.setup_configuration.steps.AdminOIDCConfigurationStep",
    "openproduct.setup_configuration.steps.ExterneVerwijzingConfigConfigurationStep",
    "openproduct.setup_configuration.steps.DmnConfigsConfigurationStep",
)

#
# Django-Admin-Index
#
ADMIN_INDEX_DISPLAY_DROP_DOWN_MENU_CONDITION_FUNCTION = (
    "openproduct.utils.django_two_factor_auth.should_display_dropdown_menu"
)

ADMIN_INDEX_SHOW_REMAINING_APPS = False

#
# reversion_compare
#
ADD_REVERSION_ADMIN = True
REVERSION_COMPARE_FOREIGN_OBJECTS_AS_ID = False
REVERSION_COMPARE_IGNORE_NOT_REGISTERED = False

#
# Django rest framework
#
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "openproduct.utils.oidc_drf_middleware.OIDCAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "openproduct.utils.schema.AutoSchema",
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_PAGINATION_CLASS": "openproduct.utils.pagination.Pagination",
    "PAGE_SIZE": 100,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "NON_FIELD_ERRORS_KEY": "model_errors",
    "DEFAULT_FILTER_BACKENDS": ["openproduct.utils.filters.FilterBackend"],
    "EXCEPTION_HANDLER": "openproduct.utils.views.exception_handler",
}

PRODUCTEN_API_VERSION = "1.2.0"
PRODUCTTYPEN_API_VERSION = "1.2.0"

PRODUCTEN_API_MAJOR_VERSION = PRODUCTEN_API_VERSION.split(".")[0]
PRODUCTTYPEN_API_MAJOR_VERSION = PRODUCTTYPEN_API_VERSION.split(".")[0]

#
# SPECTACULAR - OpenAPI schema generation
#

OPENPRODUCT_API_CONTACT_EMAIL = "support@maykinmedia.nl"
OPENPRODUCT_API_CONTACT_URL = "https://www.maykinmedia.nl"

SPECTACULAR_SETTINGS = {  # TODO: may need to be expanded.
    "SCHEMA_PATH_PREFIX": "/api/v1",
    "TITLE": "Open Product API",
    "LICENSE": {"name": "EUPL 1.2", "url": "https://opensource.org/licenses/EUPL-1.2"},
    "CONTACT": {
        "email": OPENPRODUCT_API_CONTACT_EMAIL,
        "url": OPENPRODUCT_API_CONTACT_URL,
    },
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "SERVE_INCLUDE_SCHEMA": False,
    "POSTPROCESSING_HOOKS": (
        "drf_spectacular.hooks.postprocess_schema_enums",
        "openproduct.utils.spectacular.custom_postprocessing_hook",
    ),
    "COMPONENT_SPLIT_REQUEST": True,
    "AUTHENTICATION_WHITELIST": [
        "openproduct.utils.oidc_drf_middleware.OIDCAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "GET_LIB_DOC_EXCLUDES": "openproduct.utils.spectacular.get_lib_doc_excludes",
}

# Subpath (optional)
# This environment variable can be configured during deployment.
SUBPATH = config("SUBPATH", None)
if SUBPATH:
    SUBPATH = f"/{SUBPATH.strip('/')}"

LANGUAGES = [
    ("nl", _("Dutch")),
    ("en", _("English")),
]

SITE_ID = None

PARLER_LANGUAGES = {
    None: (
        {
            "code": "nl",
        },
        {
            "code": "en",
        },
    ),
    "default": {
        "fallbacks": ["nl"],
        "hide_untranslated": False,
    },
}

FORCE_TRANSLATION_STRINGS = [
    _("A page number within the paginated result set."),
    _("Number of results to return per page."),
]

REQUIRE_URN_URL_MAPPING = config(
    "REQUIRE_URN_URL_MAPPING",
    True,
    group="Urns",
    help_text="whether an urn requires an url mapping",
)
REQUIRE_URL_URN_MAPPING = config(
    "REQUIRE_URL_URN_MAPPING",
    True,
    group="Urns",
    help_text="whether an url requires an urn mapping",
)
