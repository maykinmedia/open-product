from django.contrib import admin

from openproduct.logging.admin_tools import AuditLogInlineformset
from openproduct.producttypen.models import Proces


class ProcesInline(admin.TabularInline):
    formset = AuditLogInlineformset
    model = Proces
    extra = 1
