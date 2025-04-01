from django.contrib import admin

from openproduct.logging.admin_tools import AuditLogInlineformset
from openproduct.producttypen.models import ExterneCode


class ExterneCodeInline(admin.TabularInline):
    formset = AuditLogInlineformset
    model = ExterneCode
    extra = 1
    ordering = ("pk",)
