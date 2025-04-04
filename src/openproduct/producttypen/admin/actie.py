from django.contrib import admin

from reversion_compare.admin import CompareVersionAdmin

from openproduct.logging.admin_tools import AdminAuditLogMixin, AuditLogInlineformset
from openproduct.producttypen.models import Actie


class ActieInline(admin.TabularInline):
    formset = AuditLogInlineformset
    model = Actie
    extra = 1
    ordering = ("pk",)


@admin.register(Actie)
class ActieAdmin(AdminAuditLogMixin, CompareVersionAdmin):
    list_display = ("product_type", "naam", "url")
    list_filter = ("product_type__code", "dmn_config__naam")
