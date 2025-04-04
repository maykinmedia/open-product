from django.contrib import admin

from solo.admin import SingletonModelAdmin

from openproduct.producttypen.models import ExterneVerwijzingConfig


@admin.register(ExterneVerwijzingConfig)
class ExterneVerwijzingConfigAdmin(SingletonModelAdmin):
    pass
