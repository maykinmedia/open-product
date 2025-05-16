from django.contrib import admin

from reversion_compare.admin import CompareVersionAdmin

from openproduct.logging.admin_tools import AdminAuditLogMixin
from openproduct.producttypen.models import ExterneVerwijzingConfig


@admin.register(ExterneVerwijzingConfig)
class ExterneVerwijzingConfigAdmin(AdminAuditLogMixin, CompareVersionAdmin):
    list_display = ("naam", "basis_url")
    search_fields = ("naam", "basis_url")
