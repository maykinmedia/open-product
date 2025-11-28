"""
Bootstrap the environment.

Load the secrets from the .env file and store them in the environment, so
they are available for Django settings initialization.

.. warning::

    do NOT import anything Django related here, as this file needs to be loaded
    before Django is initialized.
"""

import os
import warnings
from pathlib import Path

from django.conf import settings

import structlog
from dotenv import load_dotenv
from maykin_common.otel import setup_otel

logger = structlog.stdlib.get_logger(__name__)


def setup_env():
    # load the environment variables containing the secrets/config
    dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(dotenv_path)

    structlog.contextvars.bind_contextvars(source="app")

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openproduct.conf.dev")
    if "OTEL_SERVICE_NAME" not in os.environ:
        warnings.warn(
            "No OTEL_SERVICE_NAME environment variable set, using a default. "
            "You should set a (distinct) value for each component (web, worker...)",
            RuntimeWarning,
            stacklevel=2,
        )
        os.environ.setdefault("OTEL_SERVICE_NAME", "openproduct")

    setup_otel()

    monkeypatch_requests()


def monkeypatch_requests():
    """
    Add a default timeout for any requests calls.

    Clean up the code by removing the try/except if requests is installed, or removing
    the call to this function in setup_env if it isn't
    """
    try:
        from requests import Session
    except ModuleNotFoundError:
        logger.debug("attempt_to_patch_requests_but_library_not_installed")
        return

    if hasattr(Session, "_original_request"):
        logger.debug("session_already_patched_or_has_original_request_attribute")
        return

    Session._original_request = Session.request

    def new_request(self, *args, **kwargs):
        kwargs.setdefault("timeout", settings.REQUESTS_DEFAULT_TIMEOUT)
        return self._original_request(*args, **kwargs)

    Session.request = new_request
