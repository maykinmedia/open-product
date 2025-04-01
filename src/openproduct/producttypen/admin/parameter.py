from django.contrib import admin

from openproduct.logging.admin_tools import AuditLogInlineformset
from openproduct.producttypen.models import Parameter


class ParameterInline(admin.TabularInline):
    formset = AuditLogInlineformset
    model = Parameter
    extra = 1
