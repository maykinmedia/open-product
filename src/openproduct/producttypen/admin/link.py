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
    list_display = ("producttype", "naam", "url")
    list_filter = ("producttype__code",)
    search_fields = ("naam", "producttype__translations__naam")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("producttype")
