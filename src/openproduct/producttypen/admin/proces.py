from django.contrib import admin

from guardian.admin import GuardedInlineAdminMixin

from openproduct.logging.admin_tools import AuditLogInlineformset
from openproduct.producttypen.models import Proces


class ProcesInline(GuardedInlineAdminMixin, admin.TabularInline):
    formset = AuditLogInlineformset
    model = Proces
    extra = 1
