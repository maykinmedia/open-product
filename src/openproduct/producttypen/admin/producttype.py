from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext as _

from ordered_model.admin import OrderedInlineModelAdminMixin
from parler.admin import TranslatableAdmin
from parler.forms import TranslatableModelForm
from reversion_compare.admin import CompareVersionAdmin

from ...logging.admin_tools import AdminAuditLogMixin
from ...utils.widgets import WysimarkWidget
from ..models import ProductType, Thema
from ..models.producttype import ProductTypeTranslation
from . import ActieInline
from .bestand import BestandInline
from .content import ContentElementInline
from .externe_code import ExterneCodeInline
from .link import LinkInline
from .parameter import ParameterInline
from .proces import ProcesInline
from .verzoektype import VerzoekTypeInline
from .zaaktype import ZaakTypeInline


@admin.register(ProductTypeTranslation)
class ProductTypeTranslationAdmin(AdminAuditLogMixin, CompareVersionAdmin):
    list_display = ("master", "naam", "language_code")
    list_filter = ("master__themas", "language_code")
    search_fields = ("naam",)
    readonly_fields = ("master", "language_code")


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
    TranslatableAdmin,
    CompareVersionAdmin,
):
    list_display = (
        "naam",
        "uniforme_product_naam",
        "aanmaak_datum",
        "display_themas",
        "gepubliceerd",
        "keywords",
    )
    list_filter = ("gepubliceerd", "themas")
    list_editable = ("gepubliceerd",)
    date_hierarchy = "aanmaak_datum"
    autocomplete_fields = (
        "organisaties",
        "contacten",
        "locaties",
        "uniforme_product_naam",
        "verbruiksobject_schema",
        "dataobject_schema",
    )
    search_fields = ("naam", "uniforme_product_naam__naam", "keywords")
    save_on_top = True
    form = ProductTypeAdminForm
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
    fields = (
        "naam",
        "gepubliceerd",
        "code",
        "uniforme_product_naam",
        "toegestane_statussen",
        "samenvatting",
        "themas",
        "verbruiksobject_schema",
        "dataobject_schema",
        "keywords",
        "interne_opmerkingen",
        "organisaties",
        "locaties",
        "contacten",
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("themas", "contacten", "locaties", "organisaties")
        )

    @admin.display(description="thema's")
    def display_themas(self, obj):
        return ", ".join(p.naam for p in obj.themas.all())
