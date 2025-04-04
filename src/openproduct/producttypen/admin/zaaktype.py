from django.contrib import admin

from openproduct.logging.admin_tools import AuditLogInlineformset
from openproduct.producttypen.models import ZaakType


class ZaakTypeInline(admin.TabularInline):
    formset = AuditLogInlineformset
    model = ZaakType
    extra = 1
