from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from reversion_compare.admin import CompareVersionAdmin

from openproduct.logging.admin_tools import AdminAuditLogMixin, AuditLogInlineformset

from ..models.facets import FacetType, FacetWaarde
from ..models.producttype import ProductType
from ..models.validators import (
    validate_meervoudig_facetten,
    validate_verplichte_facetten,
)

ProductTypeFacet = ProductType.facetten.through


class ProductTypeFacetForm(forms.ModelForm):
    facet_type = forms.ModelChoiceField(
        queryset=FacetType.objects.all(), label=_("facettype")
    )

    class Meta:
        model = ProductTypeFacet
        fields = ("facet_type", "facetwaarde")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.initial["facet_type"] = self.instance.facetwaarde.facet_type_id

        if self.is_bound:
            facet_type_id = self.data.get(self.add_prefix("facet_type"))
        else:
            facet_type_id = self.initial.get("facet_type")

        self.fields["facetwaarde"].queryset = (
            FacetWaarde.objects.filter(facet_type_id=facet_type_id)
            if str(facet_type_id or "").isdigit()
            else FacetWaarde.objects.none()
        )


class FacetInlineFormSet(AuditLogInlineformset):
    def clean(self):
        super().clean()

        facetwaarden = []
        for form in self.forms:
            if self._should_delete_form(form):
                continue

            facetwaarde = form.cleaned_data.get("facetwaarde")
            if facetwaarde:
                facetwaarden.append(facetwaarde)

        validate_meervoudig_facetten(facetwaarden)
        validate_verplichte_facetten(facetwaarden)


class FacetInline(admin.TabularInline):
    model = ProductTypeFacet
    form = ProductTypeFacetForm
    formset = FacetInlineFormSet
    extra = 1

    class Media:
        js = ("admin/js/admin/facet_inline.js",)


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
