from django.utils.translation import gettext_lazy as _

import django_filters
from drf_spectacular.utils import extend_schema, extend_schema_view
from notifications_api_common.viewsets import NotificationViewSetMixin

from openproduct.logging.api_tools import AuditTrailViewSetMixin
from openproduct.producten.kanalen import KANAAL_PRODUCTEN
from openproduct.producten.models import Product
from openproduct.producten.serializers.product import ProductSerializer
from openproduct.utils.enums import Operators
from openproduct.utils.filters import (
    FilterSet,
    ManyCharFilter,
    TranslationFilter,
    filter_data_attr_value_part,
)
from openproduct.utils.helpers import display_choice_values_for_help_text
from openproduct.utils.validators import validate_data_attr
from openproduct.utils.views import OrderedModelViewSet

DATA_ATTR_HELP_TEXT = _(
    """
Een json filter parameter heeft de format `key__operator__waarde`.
`key` is de naam van de attribuut, `operator` is de operator die gebruikt moet worden en `waarde` is de waarde waarop zal worden gezocht.

Waardes kunnen een string, nummer of datum (ISO format; YYYY-MM-DD) zijn.

De ondersteunde operators zijn:
{}

`key` mag ook geen komma's bevatten.

Voorbeeld: om producten met `kenteken`: `AA-111-B` in het dataobject vinden: `dataobject_attr=kenteken__exact__AA-111-B`.
Als `kenteken` genest zit in `auto`: `dataobject_attr=auto__kenteken__exact__AA-111-B`



Meerdere filters kunnen worden toegevoegd door `dataobject_attr` meerdere keren aan het request toe te voegen.
Bijvoorbeeld: `dataobject_attr=kenteken__exact__AA-111-B&objectdata_attr=zone__exact__B`
"""
).format(display_choice_values_for_help_text(Operators))


class ProductFilterSet(FilterSet):
    uniforme_product_naam = django_filters.CharFilter(
        field_name="product_type__uniforme_product_naam__naam",
        lookup_expr="exact",
        help_text=_("Uniforme product naam vanuit de UPL."),
    )

    product_type__naam = TranslationFilter(
        field_name="product_type__naam",
        lookup_expr="exact",
        help_text=_("Naam van het product type."),
    )

    dataobject_attr = ManyCharFilter(
        method="filter_dataobject_attr",
        validators=[validate_data_attr],
        help_text=DATA_ATTR_HELP_TEXT,
    )

    verbruiksobject_attr = ManyCharFilter(
        method="filter_verbruiksobject_attr",
        validators=[validate_data_attr],
        help_text=DATA_ATTR_HELP_TEXT,
    )

    def filter_dataobject_attr(self, queryset, name, value: list):
        for value_part in value:
            queryset = filter_data_attr_value_part(value_part, "dataobject", queryset)

        return queryset

    def filter_verbruiksobject_attr(self, queryset, name, value: list):
        for value_part in value:
            queryset = filter_data_attr_value_part(
                value_part, "verbruiksobject", queryset
            )

        return queryset

    class Meta:
        model = Product
        fields = {
            "gepubliceerd": ["exact"],
            "status": ["exact"],
            "frequentie": ["exact"],
            "prijs": ["exact", "gte", "lte"],
            "product_type__code": ["exact"],
            "product_type__id": ["exact"],
            "start_datum": ["exact", "gte", "lte"],
            "eind_datum": ["exact", "gte", "lte"],
            "aanmaak_datum": ["exact", "gte", "lte"],
            "update_datum": ["exact", "gte", "lte"],
        }


@extend_schema_view(
    list=extend_schema(
        summary="Alle PRODUCTEN opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek PRODUCT opvragen.",
    ),
    create=extend_schema(
        summary="Maak een PRODUCT aan.",
    ),
    update=extend_schema(
        summary="Werk een PRODUCT in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een PRODUCT deels bij.",
    ),
    destroy=extend_schema(
        summary="Verwijder een PRODUCT.",
    ),
)
class ProductViewSet(
    AuditTrailViewSetMixin, NotificationViewSetMixin, OrderedModelViewSet
):
    queryset = Product.objects.all()
    lookup_url_field = "id"
    serializer_class = ProductSerializer
    filterset_class = ProductFilterSet
    notifications_kanaal = KANAAL_PRODUCTEN
