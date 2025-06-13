from django.contrib import admin

from openproduct.logging.admin_tools import AuditLogInlineformset
from openproduct.producttypen.models import Actie


class ActieInline(admin.TabularInline):
    formset = AuditLogInlineformset
    model = Actie
    extra = 1
    formset = AuditLogInlineformset

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("dmn_config")


@admin.register(Actie)
class ActieAdmin(admin.ModelAdmin):
    list_display = ("producttype", "naam", "url")
    list_filter = ("producttype__code", "dmn_config__naam")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("producttype", "dmn_config")
