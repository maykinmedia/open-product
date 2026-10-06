from django.contrib import admin

from reversion_compare.admin import CompareVersionAdmin

from openproduct.logging.admin_tools import AdminAuditLogMixin, AuditLogInlineformset

from ..models.facets import FacetType, FacetWaarde


class FacetWaardeInline(admin.TabularInline):
    formset = AuditLogInlineformset
    model = FacetWaarde
    extra = 1


@admin.register(FacetType)
class FacetTypeAdmin(AdminAuditLogMixin, CompareVersionAdmin):
    list_display = (
        "naam",
        "facetteerbaar",
        "meervoudig_toegestaan",
        "verplicht",
    )
    list_filter = ("facetteerbaar", "meervoudig_toegestaan", "verplicht")
    search_fields = ("naam", "omschrijving")
    inlines = (FacetWaardeInline,)
