from django import forms
from django.contrib import admin
from django.core.exceptions import PermissionDenied
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
from openproduct.producttypen.models.enums import ProductStateChoices
from openproduct.producttypen.models.producttype import ProductType

from ...producttypen.models import ProductTypePermission
from ...producttypen.models.producttypepermission import PermissionModes
from ...urn.validators import validate_urn_or_url
from .document import DocumentInline
from .eigenaar import EigenaarInline
from .taak import TaakInline
from .zaak import ZaakInline


def get_status_choices(producttype_id, instance):
    if instance:
        return [
            choice
            for choice in ProductStateChoices.choices
            if choice[0] in instance.producttype.toegestane_statussen
            or choice[0] == ProductStateChoices.INITIEEL.value
            or choice[0] == instance.status  # keep exising status of product
        ]

    if producttype_id:
        return [
            choice
            for choice in ProductStateChoices.choices
            if choice[0]
            in ProductType.objects.get(id=producttype_id).toegestane_statussen
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
                args[0].get("producttype") if args else None, kwargs.get("instance")
            ),
            widget=forms.Select,
        )

    def clean(self):
        """
        The toegestane_statussen on the producttype should be changeable without it affecting existing products.
        This means that the status & dates should only be validated when they (or the producttype is changed) otherwise it will raise an exception.
        """
        super().clean()

        if self.errors:
            return

        validate_urn_or_url(
            self.cleaned_data["aanvraag_zaak_urn"],
            self.cleaned_data["aanvraag_zaak_url"],
            "aanvraag_zaak",
        )

        validate_product_verbruiksobject(
            self.cleaned_data["verbruiksobject"], self.cleaned_data["producttype"]
        )

        validate_product_dataobject(
            self.cleaned_data["dataobject"], self.cleaned_data["producttype"]
        )

        producttype_changed = "producttype" in self.changed_data

        if "status" in self.changed_data or producttype_changed:
            validate_product_status(
                self.cleaned_data["status"], self.cleaned_data["producttype"]
            )

        if "start_datum" in self.changed_data or producttype_changed:
            validate_product_start_datum(
                self.cleaned_data["start_datum"], self.cleaned_data["producttype"]
            )

        if "eind_datum" in self.changed_data or producttype_changed:
            validate_product_eind_datum(
                self.cleaned_data["eind_datum"], self.cleaned_data["producttype"]
            )


@admin.register(Product)
class ProductAdmin(AdminAuditLogMixin, CompareVersionAdmin):
    list_display = (
        "naam",
        "producttype",
        "aanmaak_datum",
        "start_datum",
        "eind_datum",
        "status",
        "show_actions",
    )
    list_filter = (
        "producttype__code",
        "aanmaak_datum",
        "start_datum",
        "eind_datum",
        "status",
    )
    search_fields = ("naam",)
    autocomplete_fields = ("producttype",)
    readonly_fields = ("uuid",)
    form = ProductAdminForm
    inlines = (EigenaarInline, DocumentInline, ZaakInline, TaakInline)
    list_select_related = ("producttype",)

    @admin.display(description="Producttype")
    def producttype_name(self, obj):
        return obj.producttype.naam

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

    def _has_permission(
        self, user, permission=bool, obj=None, producttype=None, write=True
    ):
        if (obj or producttype) and not user.is_superuser:
            return (
                permission
                and ProductTypePermission.objects.filter(
                    user=user,
                    producttype=producttype if producttype else obj.producttype,
                    **({"mode": PermissionModes.read_and_write} if write else {}),
                ).exists()
            )
        return permission

    def has_add_permission(self, request, obj=None):
        return self._has_permission(
            request.user, super().has_add_permission(request), obj
        )

    def has_change_permission(self, request, obj=None):
        return self._has_permission(
            request.user, super().has_change_permission(request, obj), obj
        )

    def has_view_permission(self, request, obj=None):
        return self._has_permission(
            request.user, super().has_view_permission(request, obj), obj, write=False
        )

    def has_delete_permission(self, request, obj=None):
        return self._has_permission(
            request.user, super().has_delete_permission(request, obj), obj
        )

    def save_model(self, request, obj, form, change):
        if (
            not request.user.is_superuser
            and "producttype" in form.changed_data
            and not self._has_permission(
                request.user,
                super().has_change_permission(request, obj)
                if change
                else super().has_add_permission(request),
                producttype=form.cleaned_data["producttype"],
            )
        ):
            raise PermissionDenied(
                _("You do not have permission to perform this action.")
            )

        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if not request.user.is_superuser:
            qs = qs.filter(
                producttype__in=ProductTypePermission.objects.filter(
                    user=request.user
                ).values_list("producttype", flat=True)
            )
        return qs
