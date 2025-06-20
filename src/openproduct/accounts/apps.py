from io import StringIO

from django.apps import AppConfig, apps
from django.conf import settings
from django.contrib.contenttypes.management import create_contenttypes
from django.core.management import call_command
from django.db.models.signals import post_migrate

import structlog

logger = structlog.stdlib.get_logger(__name__)


def update_admin_index(sender, **kwargs):
    if "django_admin_index" not in settings.INSTALLED_APPS:
        logger.warning("django_admin_index_not_installed_skipping_update_admin_index")
        return

    from django_admin_index.models import AppGroup

    AppGroup.objects.all().delete()

    # Make sure project models are registered.
    project_name = __name__.split(".")[0]

    for app_config in apps.get_app_configs():
        if app_config.name.startswith(project_name):
            create_contenttypes(app_config, verbosity=0)
    out = StringIO()
    try:
        call_command("loaddata", "default_admin_index", verbosity=0, stdout=out)
    except Exception as exc:
        logger.warning(
            "unable_to_load_default_admin_index_fixture_might_need_to_regenerate",
            error=str(exc),
            suggestion="run_bin_generate_admin_index_fixtures_sh",
        )
        return
    logger.info("loaded_django_admin_index_fixture", output=out.getvalue())


class AccountsConfig(AppConfig):
    name = "openproduct.accounts"

    def ready(self):
        post_migrate.connect(update_admin_index, sender=self)
