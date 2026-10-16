from django.contrib import admin

from openproduct.logging.admin_tools import AuditLogInlineformset
from openproduct.producttypen.models import SubType


class SubTypeInline(admin.TabularInline):
    model = SubType
    extra = 0
    fields = ("naam",)
    formset = AuditLogInlineformset
