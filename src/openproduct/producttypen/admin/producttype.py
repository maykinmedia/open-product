from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.urls import reverse
from django.utils.translation import gettext as _

from ordered_model.admin import OrderedInlineModelAdminMixin
from parler.forms import TranslatableModelForm
from reversion_compare.admin import CompareVersionAdmin

from openproduct.utils.admin import TranslatableAdmin
from openproduct.utils.export import ExportMixin, export_csv, export_json

from ...logging.admin_tools import AdminAuditLogMixin
from ...utils.widgets import WysimarkWidget
from ..models import ProductType, Thema
from ..models.producttype import ProductTypeTranslation
from ..models.producttypepermission import PermissionModes
from . import ActieInline
from .bestand import BestandInline
from .content import ContentElementInline
from .externe_code import ExterneCodeInline
from .filters import GepubliceerdFilter
from .link import LinkInline
from .parameter import ParameterInline
from .proces import ProcesInline
from .verzoektype import VerzoekTypeInline
from .zaaktype import ZaakTypeInline


@admin.register(ProductTypeTranslation)
class ProductTypeTranslationAdmin(AdminAuditLogMixin, CompareVersionAdmin):
    list_display = ("producttype", "language_code")
    list_filter = ("master__themas", "master__code", "language_code")
    search_fields = ("naam",)
    readonly_fields = ("master", "language_code")

    @admin.display(description="Producttype")
    def producttype(self, obj):
        return obj.master

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Translations should only be deleted by the cascade on the producttype and not by themselves.
        When a producttype is deleted via the admin this function is still called and should return True.
        """
        if reverse("admin:producttypen_producttype_changelist") in request.path:
            return True

        return False

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("master")
            .prefetch_related("master__themas")
        )


class ProductTypeAdminForm(TranslatableModelForm):
    class Meta:
        model = ProductType
        fields = "__all__"
        widgets = {
            "samenvatting": WysimarkWidget(),
            "interne_opmerkingen": WysimarkWidget(),
        }

    themas = forms.ModelMultipleChoiceField(
        label=_("thema's"),
        queryset=Thema.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(verbose_name=_("Thema"), is_stacked=False),
    )

    def clean(self):
        cleaned_data = super().clean()
        if len(cleaned_data["themas"]) == 0:
            self.add_error("themas", _("Er is minimaal één thema vereist."))
        return cleaned_data


@admin.register(ProductType)
class ProductTypeAdmin(
    AdminAuditLogMixin,
    OrderedInlineModelAdminMixin,
    ExportMixin,
    TranslatableAdmin,
    CompareVersionAdmin,
):
    list_display = (
        "naam",
        "code",
        "uniforme_product_naam",
        "aanmaak_datum",
        "display_themas",
        "gepubliceerd",
        "keywords",
    )
    list_filter = ("themas", GepubliceerdFilter)
    date_hierarchy = "aanmaak_datum"
    autocomplete_fields = (
        "organisaties",
        "contacten",
        "locaties",
        "uniforme_product_naam",
        "verbruiksobject_schema",
        "dataobject_schema",
    )
    search_fields = ("code", "uniforme_product_naam__naam", "keywords")
    save_on_top = True
    form = ProductTypeAdminForm
    export_exclude = ["producten"]
    actions = [export_csv, export_json]

    inlines = (
        BestandInline,
        LinkInline,
        ContentElementInline,
        ExterneCodeInline,
        ParameterInline,
        ActieInline,
        ProcesInline,
        ZaakTypeInline,
        VerzoekTypeInline,
    )

    readonly_fields = ("uuid",)

    fields = (
        "uuid",
        "naam",
        "code",
        "doelgroep",
        "uniforme_product_naam",
        "publicatie_start_datum",
        "publicatie_eind_datum",
        "samenvatting",
        "themas",
        "verbruiksobject_schema",
        "dataobject_schema",
        "keywords",
        "interne_opmerkingen",
        "organisaties",
        "eigenaar",
        "locaties",
        "contacten",
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("uniforme_product_naam")
            .prefetch_related("themas")
        )

    @admin.display(description="thema's")
    def display_themas(self, obj):
        return ", ".join(p.naam for p in obj.themas.all())

    def gepubliceerd(self, obj):
        return _("Ja") if obj.gepubliceerd else _("Nee")

    def get_search_results(self, request, queryset, search_term):
        queryset, may_have_duplicates = super().get_search_results(
            request, queryset, search_term
        )

        if not request.user.is_superuser and request.path == reverse(
            "admin:autocomplete"
        ):
            queryset = queryset.filter(
                producttype_permissions__user=request.user,
                producttype_permissions__mode=PermissionModes.read_and_write,
            )

        return queryset, may_have_duplicates
