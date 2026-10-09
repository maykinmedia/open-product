from django.utils.translation import gettext_lazy as _

from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.viewsets import ReadOnlyModelViewSet

from openproduct.logging.api_tools import AuditTrailRetrieveMixin
from openproduct.producttypen.models import FacetType
from openproduct.producttypen.serializers import FacetTypeSerializer


class FacetTypeFilterSet(filters.FilterSet):
    waarden__uuid = filters.UUIDFilter(
        field_name="waarden__uuid",
        help_text=_("Facettypes met een facetwaarde met deze uuid"),
    )
    waarden__naam = filters.CharFilter(
        field_name="waarden__naam",
        help_text=_("Filter facettypes op basis van de naam van een facetwaarde."),
    )
    waarden__actief = filters.BooleanFilter(
        field_name="waarden__actief",
        help_text=_(
            "Filter facettypes op basis van de actieve status van een facetwaarde."
        ),
    )

    class Meta:
        model = FacetType
        fields = {
            "uuid": ["exact"],
            "naam": ["iexact"],
            "facetteerbaar": ["exact"],
            "meervoudig_toegestaan": ["exact"],
            "verplicht": ["exact"],
        }


@extend_schema_view(
    list=extend_schema(
        summary="Alle facetten opvragen.",
        description="Deze lijst kan gefilterd worden met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifieke facet opvragen.",
    ),
)
class FacetTypeViewSet(AuditTrailRetrieveMixin, ReadOnlyModelViewSet):
    queryset = FacetType.objects.all()
    serializer_class = FacetTypeSerializer
    lookup_field = "uuid"
    filterset_class = FacetTypeFilterSet
