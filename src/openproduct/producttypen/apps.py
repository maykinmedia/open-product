from django.apps import AppConfig

from drf_spectacular.extensions import OpenApiFilterExtension


class ProducttypenConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "openproduct.producttypen"

    def ready(self):
        # load the signal receivers
        from . import signals  # noqa
        import openproduct.patches.django_otp_admin  # noqa

        unregister_camelize_filter_extension()


def unregister_camelize_filter_extension():
    """
    CamelizeFilterExtension from vng_api_common is loaded automatically and cannot be removed using SPECTACULAR_SETTINGS.
    """
    OpenApiFilterExtension._registry = [
        ext
        for ext in OpenApiFilterExtension._registry
        if ext.__name__ != "CamelizeFilterExtension"
    ]
