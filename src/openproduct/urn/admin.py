from django.contrib import admin

from openproduct.urn.models import UrnMappingConfig


@admin.register(UrnMappingConfig)
class UrnMappingConfigAdmin(admin.ModelAdmin):
    pass
