from django.utils.translation import gettext_lazy as _

import django_filters
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.viewsets import ModelViewSet
from vng_api_common.utils import get_help_text

from openproduct.logging.api_tools import AuditTrailViewSetMixin
from openproduct.producttypen.models import Prijs
from openproduct.producttypen.serializers import PrijsSerializer
from openproduct.utils.filters import FilterSet, TranslationFilter


class PrijsFilterSet(FilterSet):
    uniforme_product_naam = django_filters.CharFilter(
        field_name="producttype__uniforme_product_naam__naam",
        lookup_expr="exact",
        help_text=get_help_text("producttypen.UniformeProductNaam", "naam"),
    )

    producttype__naam = TranslationFilter(
        field_name="producttype__naam",
        lookup_expr="exact",
        help_text=_("De Nederlandse naam van het producttype"),
    )

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).distinct()

    class Meta:
        model = Prijs
        fields = {
            "producttype__uuid": ["exact"],
            "producttype__code": ["exact"],
            "actief_vanaf": ["exact", "gte", "lte"],
            "prijsopties__bedrag": ["exact", "gte", "lte"],
            "prijsopties__beschrijving": ["exact"],
            "prijsregels__dmn_tabel_id": ["exact"],
            "prijsregels__beschrijving": ["exact"],
        }


@extend_schema_view(
    list=extend_schema(
        summary="Alle PRIJZEN opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifieke PRIJS opvragen.",
    ),
    create=extend_schema(summary="Maak een PRIJS aan."),
    update=extend_schema(
        summary="Werk een PRIJS in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een PRIJS deels bij.",
    ),
    destroy=extend_schema(
        summary="Verwijder een PRIJS.",
    ),
)
class PrijsViewSet(AuditTrailViewSetMixin, ModelViewSet):
    queryset = Prijs.objects.all()
    serializer_class = PrijsSerializer
    lookup_field = "uuid"
    filterset_class = PrijsFilterSet
