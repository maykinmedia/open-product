from django.utils.translation import gettext_lazy as _

from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.viewsets import ModelViewSet

from openproduct.logging.api_tools import AuditTrailViewSetMixin
from openproduct.producttypen.models import FacetType
from openproduct.producttypen.serializers import FacetTypeSerializer


class FacetTypeFilterSet(filters.FilterSet):
    waarden__uuid = filters.UUIDFilter(
        field_name="waarden__uuid",
        help_text=_("Facettypes met een facetwaarde met deze uuid"),
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
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifieke facet opvragen.",
    ),
    create=extend_schema(
        summary="Maak een facet aan.",
    ),
    update=extend_schema(
        summary="Werk een facet in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een facet deels bij.",
    ),
    destroy=extend_schema(
        summary="Verwijder een facet.",
    ),
)
class FacetTypeViewSet(AuditTrailViewSetMixin, ModelViewSet):
    queryset = FacetType.objects.all()
    serializer_class = FacetTypeSerializer
    lookup_field = "uuid"
    filterset_class = FacetTypeFilterSet
