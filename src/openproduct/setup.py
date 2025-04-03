"""
Bootstrap the environment.

Load the secrets from the .env file and store them in the environment, so
they are available for Django settings initialization.

.. warning::

    do NOT import anything Django related here, as this file needs to be loaded
    before Django is initialized.
"""

import logging
import os
from pathlib import Path

from django.conf import settings

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def setup_env():
    # load the environment variables containing the secrets/config
    dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(dotenv_path)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openproduct.conf.dev")

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
        logger.debug("Attempt to patch requests, but the library is not installed")
        return

    if hasattr(Session, "_original_request"):
        logger.debug(
            "Session is already patched OR has an ``_original_request`` attribute."
        )
        return

    Session._original_request = Session.request

    def new_request(self, *args, **kwargs):
        kwargs.setdefault("timeout", settings.REQUESTS_DEFAULT_TIMEOUT)
        return self._original_request(*args, **kwargs)

    Session.request = new_request
