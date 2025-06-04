from django.contrib import admin

from openproduct.logging.admin_tools import AuditLogInlineformset
from openproduct.producten.models import Taak


class TaakInline(admin.TabularInline):
    formset = AuditLogInlineformset
    model = Taak
    extra = 1
