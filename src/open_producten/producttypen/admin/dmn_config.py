from django.contrib import admin

from open_producten.producttypen.models.dmn_config import DmnConfig


@admin.register(DmnConfig)
class DmnConfigAdmin(admin.ModelAdmin):
    list_display = ("naam", "tabel_endpoint")
    search_fields = ("naam", "tabel_endpoint")
