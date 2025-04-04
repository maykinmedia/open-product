from django.contrib import admin

from openproduct.producttypen.models import Actie


class ActieInline(admin.TabularInline):
    model = Actie
    extra = 1
    ordering = ("pk",)


@admin.register(Actie)
class ActieAdmin(admin.ModelAdmin):
    list_display = ("producttype", "naam", "url")
    list_filter = ("producttype__code", "dmn_config__naam")
