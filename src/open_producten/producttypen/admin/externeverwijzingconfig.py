from django.contrib import admin

from solo.admin import SingletonModelAdmin

from open_producten.producttypen.models import ExterneVerwijzingConfig


@admin.register(ExterneVerwijzingConfig)
class ExterneVerwijzingConfig(SingletonModelAdmin):
    pass
