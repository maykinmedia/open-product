from django import forms
from django.contrib import admin
from django.utils.html import format_html_join
from django.utils.translation import gettext_lazy as _

from reversion_compare.admin import CompareVersionAdmin

from openproduct.logging.service import AdminAuditLogMixin, get_logs_link
from openproduct.producten.models import Product
from openproduct.producten.models.validators import (
    validate_product_dataobject,
    validate_product_eind_datum,
    validate_product_start_datum,
    validate_product_status,
    validate_product_verbruiksobject,
)
from openproduct.producttypen.models.producttype import ProductStateChoices, ProductType

from .eigenaar import EigenaarInline


def get_status_choices(product_type_id, instance):

    if instance:
        return [
            choice
            for choice in ProductStateChoices.choices
            if choice[0] in instance.product_type.toegestane_statussen
            or choice[0] == ProductStateChoices.INITIEEL.value
            or choice[0] == instance.status  # keep exising status of product
        ]

    if product_type_id:
        return [
            choice
            for choice in ProductStateChoices.choices
            if choice[0]
            in ProductType.objects.get(id=product_type_id).toegestane_statussen
            or choice[0] == ProductStateChoices.INITIEEL.value
        ]

    return ProductStateChoices.choices


class ProductAdminForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["status"] = forms.TypedChoiceField(
            label=_("status"),
            choices=get_status_choices(
                args[0].get("product_type") if args else None, kwargs.get("instance")
            ),
            widget=forms.Select,
        )

    def clean(self):
        """
        The toegestane_statussen on the product type should be changeable without it affecting existing products.
        This means that the status & dates should only be validated when they (or the product type is changed) otherwise it will raise an exception.
        """
        super().clean()

        if self.errors:
            return

        validate_product_verbruiksobject(
            self.cleaned_data["verbruiksobject"], self.cleaned_data["product_type"]
        )

        validate_product_dataobject(
            self.cleaned_data["dataobject"], self.cleaned_data["product_type"]
        )

        product_type_changed = "product_type" in self.changed_data

        if "status" in self.changed_data or product_type_changed:
            validate_product_status(
                self.cleaned_data["status"], self.cleaned_data["product_type"]
            )

        if "start_datum" in self.changed_data or product_type_changed:
            validate_product_start_datum(
                self.cleaned_data["start_datum"], self.cleaned_data["product_type"]
            )

        if "eind_datum" in self.changed_data or product_type_changed:
            validate_product_eind_datum(
                self.cleaned_data["eind_datum"], self.cleaned_data["product_type"]
            )


@admin.register(Product)
class ProductAdmin(AdminAuditLogMixin, CompareVersionAdmin):
    list_display = (
        "product_type_name",
        "aanmaak_datum",
        "start_datum",
        "eind_datum",
        "status",
        "show_actions",
    )
    list_filter = (
        ("product_type__translations__naam"),
        "aanmaak_datum",
        "start_datum",
        "eind_datum",
        "status",
    )
    autocomplete_fields = ("product_type",)
    search_fields = ("product_type__translations__naam",)
    form = ProductAdminForm
    inlines = (EigenaarInline,)

    @admin.display(description="Product Type")
    def product_type_name(self, obj):
        return obj.product_type.naam

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("product_type")

    @admin.display(description=_("acties"))
    def show_actions(self, obj: Product) -> str:
        actions = [
            get_logs_link(obj),
        ]
        return format_html_join(
            " | ",
            '<a href="{}">{}</a>',
            actions,
        )
