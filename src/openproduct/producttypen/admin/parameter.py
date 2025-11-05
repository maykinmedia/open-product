from django.contrib import admin

from guardian.admin import GuardedInlineAdminMixin

from openproduct.logging.admin_tools import AuditLogInlineformset
from openproduct.producttypen.models import Parameter


class ParameterInline(GuardedInlineAdminMixin, admin.TabularInline):
    formset = AuditLogInlineformset
    model = Parameter
    extra = 1
