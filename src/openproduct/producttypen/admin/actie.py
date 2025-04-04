from django.contrib import admin

from openproduct.producttypen.models import Actie


class ActieInline(admin.TabularInline):
    model = Actie
    extra = 1
    ordering = ("pk",)


@admin.register(Actie)
class ActieAdmin(admin.ModelAdmin):
    list_display = ("product_type", "naam", "url")
    list_filter = ("product_type__code", "dmn_config__naam")
