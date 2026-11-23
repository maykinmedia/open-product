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
from collections.abc import Callable
from functools import wraps
from pathlib import Path

from django.conf import settings

import structlog
from dotenv import load_dotenv
from maykin_common.otel import setup_otel

logger = structlog.stdlib.get_logger(__name__)
_timeout_sentinel = object()


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
        logger.debug(
            "requests_patching_failed", reason="requests library not installed"
        )
        return

    marking_attr = "_timeout_monkeypatched"

    if (mark := getattr(Session, marking_attr, None)) is not None:
        if mark is _timeout_sentinel:
            logger.debug(
                "requests_patching_skipped", reason="Session is already patched"
            )
        else:
            logger.debug(
                "requests_patching_skipped",
                reason=(
                    f"Session.{marking_attr} was set by code other than this module, "
                    "e.g. a copy of this patch"
                ),
            )
        return

    setattr(Session, marking_attr, _timeout_sentinel)

    def decorate[**P, R](func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def new_request(*args: P.args, **kwargs: P.kwargs) -> R:
            kwargs.setdefault("timeout", settings.REQUESTS_DEFAULT_TIMEOUT)
            return func(*args, **kwargs)

        return new_request

    Session.request = decorate(Session.request)
