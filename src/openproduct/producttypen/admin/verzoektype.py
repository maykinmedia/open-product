from django.contrib import admin

from guardian.admin import GuardedInlineAdminMixin

from openproduct.logging.admin_tools import AuditLogInlineformset
from openproduct.producttypen.models import VerzoekType


class VerzoekTypeInline(GuardedInlineAdminMixin, admin.TabularInline):
    formset = AuditLogInlineformset
    model = VerzoekType
    extra = 1
