from django.contrib import admin

from reversion_compare.admin import CompareVersionAdmin

from ...logging.admin_tools import AdminAuditLogMixin
from ..models import Contact


@admin.register(Contact)
class ContactAdmin(AdminAuditLogMixin, CompareVersionAdmin):
    list_display = ("__str__", "organisatie")
    list_filter = ("organisatie", "organisatie__stad")
    search_fields = ("naam", "organisatie__naam")
    readonly_fields = ("uuid",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("organisatie")
