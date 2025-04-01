from django.contrib import admin

from reversion_compare.admin import CompareVersionAdmin

from ...logging.admin_tools import AdminAuditLogMixin
from ..models import Locatie


@admin.register(Locatie)
class LocatieAdmin(AdminAuditLogMixin, CompareVersionAdmin):
    list_display = ("naam", "stad", "postcode", "straat", "huisnummer")
    list_filter = ("stad",)
    search_fields = ("naam", "stad", "postcode", "straat")
