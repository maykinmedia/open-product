from django.contrib import admin

from openproduct.logging.admin_tools import AuditLogInlineformset
from openproduct.producttypen.models import VerzoekType


class VerzoekTypeInline(admin.TabularInline):
    formset = AuditLogInlineformset
    model = VerzoekType
    extra = 1
