from django import forms
from django.contrib import admin, messages
from django.contrib.admin.utils import unquote
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from reversion_compare.admin import CompareVersionAdmin

from openproduct.logging.admin_tools import AdminAuditLogMixin, AuditLogInlineformset

from ..models.facets import FacetType, FacetWaarde, ProductTypeFacet
from ..models.validators import (
    check_verplichte_facetwaarden_delete,
    validate_meervoudige_facetten,
    validate_verplichte_facetten,
)


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
            FacetWaarde.objects.filter(facet_type_id=facet_type_id).select_related(
                "facet_type"
            )
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

        validate_meervoudige_facetten(facetwaarden)
        validate_verplichte_facetten(facetwaarden)


class FacetInline(admin.TabularInline):
    model = ProductTypeFacet
    form = ProductTypeFacetForm
    formset = FacetInlineFormSet
    extra = 1

    class Media:
        js = ("admin/js/admin/facet_inline.js",)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("producttype", "facetwaarde__facet_type")
        )


class FacetWaardeInline(admin.TabularInline):
    formset = AuditLogInlineformset
    model = FacetWaarde
    extra = 1
    can_delete = False  # inline delete has no confirmation page
    show_change_link = True

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("facet_type")


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


@admin.register(FacetWaarde)
class FacetWaardeAdmin(AdminAuditLogMixin, CompareVersionAdmin):
    actions = []
    list_select_related = ("facet_type",)

    def delete_view(self, request, object_id, extra_context=None):
        obj = self.get_object(request, unquote(object_id))
        if obj is not None:
            try:
                check_verplichte_facetwaarden_delete(
                    obj.facet_type, [obj], obj.facet_type.verplicht
                )
            except ValidationError as e:
                for message in e.messages:
                    self.message_user(request, message, messages.ERROR)
                return redirect(
                    "admin:producttypen_facetwaarde_change", object_id=obj.pk
                )

        return super().delete_view(request, object_id, extra_context)
