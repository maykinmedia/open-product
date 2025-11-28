from django.apps import AppConfig


class ProductenConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "openproduct.producten"

    def ready(self):
        from . import metrics  # noqa
