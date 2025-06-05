from django.contrib import admin

from openproduct.logging.admin_tools import AuditLogInlineformset
from openproduct.producten.models import Zaak


class ZaakInline(admin.TabularInline):
    formset = AuditLogInlineformset
    model = Zaak
    extra = 1
