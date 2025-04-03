import logging
from io import StringIO

from django.apps import AppConfig, apps
from django.conf import settings
from django.contrib.contenttypes.management import create_contenttypes
from django.core.management import call_command
from django.db.models.signals import post_migrate

logger = logging.getLogger(__name__)


def update_admin_index(sender, **kwargs):
    if "django_admin_index" not in settings.INSTALLED_APPS:
        logger.warning(
            "django_admin_index is not installed: skipping update_admin_index()"
        )
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
            f"Unable to load default_admin_index fixture ({exc}). You might have to regenerate the fixtures through 'bin/generate_admin_index_fixtures.sh'"
        )
        return
    logger.info("Loaded django-admin-index fixture:\n%s", out.getvalue())


class AccountsConfig(AppConfig):
    name = "openproduct.accounts"

    def ready(self):
        post_migrate.connect(update_admin_index, sender=self)
