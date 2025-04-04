from django.contrib import admin

from reversion_compare.admin import CompareVersionAdmin

from ...logging.admin_tools import AdminAuditLogMixin, AuditLogInlineformset
from ..models import Link


class LinkInline(admin.TabularInline):
    formset = AuditLogInlineformset
    model = Link
    extra = 1
    ordering = ("pk",)


@admin.register(Link)
class LinkAdmin(AdminAuditLogMixin, CompareVersionAdmin):
    list_display = ("product_type", "naam", "url")
    list_filter = ("product_type__code",)
    search_fields = ("naam", "url")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("product_type")
