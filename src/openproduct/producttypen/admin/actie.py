from django.contrib import admin

from openproduct.logging.admin_tools import AuditLogInlineformset
from openproduct.producttypen.models import Actie


class ActieInline(admin.TabularInline):
    formset = AuditLogInlineformset
    model = Actie
    extra = 1
    formset = AuditLogInlineformset


@admin.register(Actie)
class ActieAdmin(admin.ModelAdmin):
    list_display = ("producttype", "naam", "url")
    list_filter = ("producttype__code", "dmn_config__naam")

    readonly_fields = ("uuid",)
