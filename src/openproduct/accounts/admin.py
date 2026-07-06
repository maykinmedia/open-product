from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as _UserAdmin

from maykin_common.accounts.admin import PreventPrivilegeEscalationMixin

from ..producttypen.admin.producttypepermission import ProductTypePermissionInline
from .models import User


@admin.register(User)
class UserAdmin(PreventPrivilegeEscalationMixin, _UserAdmin):
    inlines = (ProductTypePermissionInline,)

    def get_inlines(self, request, obj=None):
        return self.inlines if obj else ()
