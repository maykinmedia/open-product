from datetime import date

from django import forms
from django.contrib import admin

from ..models import Prijs, PrijsOptie
from ..models.prijs import PrijsRegel, validate_optie_xor_regel


class PrijsOptieInline(admin.TabularInline):
    model = PrijsOptie
    extra = 1
    ordering = ("beschrijving",)


class PrijsRegelInline(admin.TabularInline):
    model = PrijsRegel
    extra = 1


class PrijsAdminForm(forms.ModelForm):

    class Meta:
        model = Prijs
        fields = "__all__"

    def get_entry_count(self, inline: str, unique_field: str) -> int:
        assert self.data.get(f"{inline}-0-{unique_field}") is not None

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

        regel_count = self.get_entry_count("prijsregels", "dmn_url")
        opties_count = self.get_entry_count("prijsopties", "bedrag")

        validate_optie_xor_regel(regel_count, opties_count)


@admin.register(Prijs)
class PrijsAdmin(admin.ModelAdmin):
    model = Prijs
    inlines = [PrijsOptieInline, PrijsRegelInline]
    list_display = ("__str__", "actief_vanaf")
    list_filter = ("product_type__code", "actief_vanaf")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("product_type")

    def has_change_permission(self, request, obj=None):
        if obj and obj.actief_vanaf < date.today():
            return False
        return super().has_change_permission(request, obj)
