from django.contrib import admin

from guardian.admin import GuardedInlineAdminMixin

from openproduct.logging.admin_tools import AuditLogInlineformset
from openproduct.producttypen.models import ZaakType


class ZaakTypeInline(GuardedInlineAdminMixin, admin.TabularInline):
    formset = AuditLogInlineformset
    model = ZaakType
    extra = 1
