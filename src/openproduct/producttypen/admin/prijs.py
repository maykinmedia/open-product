from datetime import date

from django import forms
from django.contrib import admin

from reversion_compare.admin import CompareVersionAdmin

from openproduct.producttypen.models.validators import validate_prijs_optie_xor_regel

from ...logging.admin_tools import AdminAuditLogMixin, AuditLogInlineformset
from ..models import Prijs, PrijsOptie
from ..models.prijs import PrijsRegel


class PrijsOptieInline(admin.TabularInline):
    model = PrijsOptie
    extra = 1
    fields = ("bedrag", "beschrijving")
    formset = AuditLogInlineformset


class PrijsRegelInline(admin.TabularInline):
    model = PrijsRegel
    autocomplete_fields = ("dmn_config",)
    extra = 1
    fields = ("dmn_config", "dmn_tabel_id", "beschrijving")
    formset = AuditLogInlineformset


class PrijsAdminForm(forms.ModelForm):

    class Meta:
        model = Prijs
        fields = "__all__"

    def get_entry_count(self, inline: str, unique_field: str) -> int:

        count = 0
        for i in range(int(self.data.get(f"{inline}-TOTAL_FORMS"))):
            if (
                self.data[f"{inline}-{i}-{unique_field}"]
                and self.data.get(f"{inline}-{i}-DELETE") != "on"
            ):
                count += 1
        return count

    def clean(self):
        super().clean()
        if self.errors:
            return

        regel_count = self.get_entry_count("prijsregels", "dmn_tabel_id")
        opties_count = self.get_entry_count("prijsopties", "bedrag")

        validate_prijs_optie_xor_regel(regel_count, opties_count)


@admin.register(Prijs)
class PrijsAdmin(AdminAuditLogMixin, CompareVersionAdmin):
    model = Prijs
    form = PrijsAdminForm
    inlines = [PrijsOptieInline, PrijsRegelInline]
    list_display = ("__str__", "actief_vanaf")
    list_filter = ("producttype__code", "actief_vanaf")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("producttype")

    def has_change_permission(self, request, obj=None):
        if obj and obj.actief_vanaf < date.today():
            return False
        return super().has_change_permission(request, obj)
