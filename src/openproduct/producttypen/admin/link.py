from django.contrib import admin

from reversion_compare.admin import CompareVersionAdmin

from ...logging.admin_tools import AdminAuditLogMixin, AuditLogInlineformset
from ..models import Link


class LinkInline(admin.TabularInline):
    formset = AuditLogInlineformset
    model = Link
    extra = 1


@admin.register(Link)
class LinkAdmin(AdminAuditLogMixin, CompareVersionAdmin):
    list_display = ("naam", "producttype", "url")
    list_filter = ("producttype__code",)
    list_select_related = ("producttype",)
    search_fields = ("naam", "url")

    readonly_fields = ("uuid",)
