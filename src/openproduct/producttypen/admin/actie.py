from django.contrib import admin

from guardian.admin import GuardedInlineAdminMixin

from openproduct.logging.admin_tools import AuditLogInlineformset
from openproduct.producttypen.models import Actie
from openproduct.utils.guardian import GuardedModelAdminMixin


class ActieInline(GuardedInlineAdminMixin, admin.TabularInline):
    formset = AuditLogInlineformset
    model = Actie
    extra = 1
    formset = AuditLogInlineformset

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("dmn_config")


@admin.register(Actie)
class ActieAdmin(GuardedModelAdminMixin, admin.ModelAdmin):
    list_display = ("naam", "producttype", "__str__", "url")
    list_filter = ("producttype__code", "dmn_config__naam")
    list_select_related = ("producttype", "dmn_config")
    search_fields = ("naam",)

    readonly_fields = ("uuid",)
