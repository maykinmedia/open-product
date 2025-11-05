from django.contrib import admin

from guardian.admin import GuardedInlineAdminMixin
from reversion_compare.admin import CompareVersionAdmin

from ...logging.admin_tools import AdminAuditLogMixin, AuditLogInlineformset
from ..models import Bestand


class BestandInline(GuardedInlineAdminMixin, admin.TabularInline):
    formset = AuditLogInlineformset
    model = Bestand
    extra = 1


@admin.register(Bestand)
class BestandAdmin(AdminAuditLogMixin, CompareVersionAdmin):
    list_display = ("bestand", "producttype")
    list_filter = ("producttype__code",)
    list_select_related = ("producttype",)
    search_fields = ("bestand",)
    readonly_fields = ("uuid",)
