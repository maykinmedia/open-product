from django.utils.translation import gettext_lazy as _

import django_filters
import structlog
from drf_spectacular.utils import extend_schema, extend_schema_view
from notifications_api_common.viewsets import NotificationViewSetMixin
from rest_framework.viewsets import ModelViewSet
from vng_api_common.utils import get_help_text

from openproduct.logging.api_tools import AuditTrailViewSetMixin
from openproduct.producten.kanalen import KANAAL_PRODUCTEN
from openproduct.producten.models import Product
from openproduct.producten.serializers.product import ProductSerializer
from openproduct.producttypen.models import ExterneVerwijzingConfig
from openproduct.utils.enums import Operators
from openproduct.utils.filters import (
    CharArrayFilter,
    FilterSet,
    ManyCharFilter,
    TranslationFilter,
    TranslationInFilter,
    UUIDFInFilter,
    filter_data_attr_value_part,
)
from openproduct.utils.helpers import display_choice_values_for_help_text
from openproduct.utils.validators import validate_data_attr

logger = structlog.stdlib.get_logger(__name__)

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
        field_name="producttype__uniforme_product_naam__naam",
        lookup_expr="exact",
        help_text=get_help_text("producttypen.UniformeProductNaam", "naam"),
    )

    producttype__naam = TranslationFilter(
        field_name="producttype__naam",
        lookup_expr="exact",
        help_text=get_help_text("producttypen.ProductTypeTranslation", "naam"),
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

    producttype__naam__in = TranslationInFilter(
        field_name="producttype__naam",
        help_text=get_help_text("producttypen.ProductTypeTranslation", "naam"),
    )

    eigenaren__bsn = django_filters.CharFilter(
        field_name="eigenaren__bsn",
        lookup_expr="exact",
        distinct=True,
        help_text=get_help_text("producten.eigenaar", "bsn"),
    )

    eigenaren__kvk_nummer = django_filters.CharFilter(
        field_name="eigenaren__kvk_nummer",
        lookup_expr="exact",
        distinct=True,
        help_text=get_help_text("producten.eigenaar", "kvk_nummer"),
    )

    eigenaren__vestigingsnummer = django_filters.CharFilter(
        field_name="eigenaren__vestigingsnummer",
        lookup_expr="exact",
        distinct=True,
        help_text=get_help_text("producten.eigenaar", "vestigingsnummer"),
    )

    eigenaren__klantnummer = django_filters.CharFilter(
        field_name="eigenaren__klantnummer",
        lookup_expr="exact",
        distinct=True,
        help_text=get_help_text("producten.eigenaar", "klantnummer"),
    )

    producttype__themas__naam__in = CharArrayFilter(
        field_name="producttype__themas__naam",
        distinct=True,
        help_text=_("Lijst van thema namen waarop kan worden gezocht."),
    )

    producttype__themas__uuid__in = UUIDFInFilter(
        field_name="producttype__themas__uuid",
        distinct=True,
        help_text=_("Lijst van thema uuids waarop kan worden gezocht."),
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
            "producttype__code": ["exact", "in"],
            "producttype__uuid": ["exact", "in"],
            "producttype__themas__naam": ["exact"],
            "producttype__themas__uuid": ["exact"],
            "naam": ["exact"],
            "start_datum": ["exact", "gte", "lte"],
            "eind_datum": ["exact", "gte", "lte"],
            "aanmaak_datum": ["exact", "gte", "lte"],
            "update_datum": ["exact", "gte", "lte"],
            "documenten__uuid": ["exact"],
            "zaken__uuid": ["exact"],
            "taken__uuid": ["exact"],
            "eigenaren__uuid": ["exact"],
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
class ProductViewSet(AuditTrailViewSetMixin, NotificationViewSetMixin, ModelViewSet):
    queryset = Product.objects.all()
    lookup_field = "uuid"
    serializer_class = ProductSerializer
    filterset_class = ProductFilterSet
    notifications_kanaal = KANAAL_PRODUCTEN

    def get_serializer_context(self):
        context = super().get_serializer_context()
        externe_verwijzing_config = ExterneVerwijzingConfig.get_solo()

        if not all(
            (
                externe_verwijzing_config.documenten_url,
                externe_verwijzing_config.zaken_url,
                externe_verwijzing_config.taken_url,
            )
        ):
            logger.warning(
                "een_of_meerdere_urls_niet_geconfigureerd_in_externe_verwijzing_config"
            )

        context["externe_verwijzing_config"] = externe_verwijzing_config
        return context
