from django.utils.translation import gettext_lazy as _

import django_filters
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.parsers import MultiPartParser

from openproduct.producttypen.models import Bestand
from openproduct.producttypen.serializers import BestandSerializer
from openproduct.utils.filters import FilterSet, TranslationFilter
from openproduct.utils.views import OrderedModelViewSet


class BestandFilterSet(FilterSet):
    uniforme_product_naam = django_filters.CharFilter(
        field_name="product_type__uniforme_product_naam__naam",
        lookup_expr="exact",
        help_text=_("Uniforme product naam vanuit de UPL."),
    )
    naam__contains = django_filters.CharFilter(
        field_name="bestand",
        lookup_expr="contains",
        help_text=_("Naam van het bestand."),
    )

    product_type__naam = TranslationFilter(
        field_name="product_type__naam",
        lookup_expr="exact",
        help_text=_("Naam van het product type."),
    )

    class Meta:
        model = Bestand
        fields = {
            "product_type__code": ["exact"],
            "product_type__id": ["exact"],
        }


@extend_schema_view(
    list=extend_schema(
        summary="Alle BESTANDEN opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek BESTAND opvragen.",
    ),
    create=extend_schema(
        summary="Maak een BESTAND aan.",
    ),
    update=extend_schema(
        summary="Werk een BESTAND in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een BESTAND deels bij.",
    ),
    destroy=extend_schema(
        summary="Verwijder een BESTAND.",
    ),
)
class BestandViewSet(OrderedModelViewSet):
    queryset = Bestand.objects.all()
    parser_classes = [MultiPartParser]
    serializer_class = BestandSerializer
    lookup_url_kwarg = "id"
    filterset_class = BestandFilterSet
