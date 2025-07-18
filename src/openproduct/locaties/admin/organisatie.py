from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from reversion_compare.admin import CompareVersionAdmin

from ...logging.admin_tools import AdminAuditLogMixin
from ..models import Organisatie


@admin.register(Organisatie)
class OrganisatieAdmin(AdminAuditLogMixin, CompareVersionAdmin):
    list_display = ("naam",)
    list_filter = ("stad",)
    search_fields = ("naam", "stad", "postcode", "straat")

    readonly_fields = ("uuid",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "uuid",
                    "naam",
                )
            },
        ),
        (_("Contact"), {"fields": ("email", "telefoonnummer")}),
        (
            _("Adres"),
            {"fields": ("straat", "huisnummer", "postcode", "stad")},
        ),
    )
