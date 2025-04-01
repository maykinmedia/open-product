from django.contrib import admin

from reversion_compare.admin import CompareVersionAdmin

from openproduct.logging.admin_tools import AdminAuditLogMixin
from openproduct.producttypen.models.dmn_config import DmnConfig


@admin.register(DmnConfig)
class DmnConfigAdmin(AdminAuditLogMixin, CompareVersionAdmin):
    list_display = ("naam", "tabel_endpoint")
    search_fields = ("naam", "tabel_endpoint")
