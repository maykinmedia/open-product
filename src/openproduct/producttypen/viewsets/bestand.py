from django.utils.translation import gettext_lazy as _

import django_filters
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.parsers import MultiPartParser

from openproduct.logging.api_tools import AuditTrailViewSetMixin
from openproduct.producttypen.models import Bestand
from openproduct.producttypen.serializers import BestandSerializer
from openproduct.utils.filters import FilterSet, TranslationFilter
from openproduct.utils.views import OrderedModelViewSet


class BestandFilterSet(FilterSet):
    uniforme_product_naam = django_filters.CharFilter(
        field_name="producttype__uniforme_product_naam__naam",
        lookup_expr="exact",
        help_text=_("Uniforme product naam vanuit de UPL."),
    )
    naam__contains = django_filters.CharFilter(
        field_name="bestand",
        lookup_expr="contains",
        help_text=_("Naam van het bestand."),
    )

    producttype__naam = TranslationFilter(
        field_name="producttype__naam",
        lookup_expr="exact",
        help_text=_("Naam van het producttype."),
    )

    class Meta:
        model = Bestand
        fields = {
            "producttype__code": ["exact"],
            "producttype__uuid": ["exact"],
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
class BestandViewSet(AuditTrailViewSetMixin, OrderedModelViewSet):
    queryset = Bestand.objects.all()
    parser_classes = [MultiPartParser]
    serializer_class = BestandSerializer
    lookup_field = "uuid"
    filterset_class = BestandFilterSet
