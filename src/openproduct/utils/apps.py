from django.apps import AppConfig


class UtilsConfig(AppConfig):
    name = "openproduct.utils"

    def ready(self):
        from . import checks  # noqa
