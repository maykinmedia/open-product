from django.contrib import admin

from guardian.admin import GuardedInlineAdminMixin

from openproduct.logging.admin_tools import AuditLogInlineformset
from openproduct.producttypen.models import ExterneCode


class ExterneCodeInline(GuardedInlineAdminMixin, admin.TabularInline):
    formset = AuditLogInlineformset
    model = ExterneCode
    extra = 1
