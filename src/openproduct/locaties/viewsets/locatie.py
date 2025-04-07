from drf_spectacular.utils import extend_schema, extend_schema_view

from openproduct.locaties.models import Locatie
from openproduct.locaties.serializers import LocatieSerializer
from openproduct.logging.api_tools import AuditTrailViewSetMixin
from openproduct.utils.filters import FilterSet
from openproduct.utils.views import OrderedModelViewSet


class LocatieFilterSet(FilterSet):

    class Meta:
        model = Locatie
        fields = {
            "naam": ["iexact"],
            "email": ["iexact"],
            "telefoonnummer": ["contains"],
            "straat": ["iexact"],
            "huisnummer": ["iexact"],
            "postcode": ["exact"],
            "stad": ["exact"],
        }


@extend_schema_view(
    list=extend_schema(
        summary="Alle LOCATIES opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifieke LOCATIE opvragen.",
    ),
    create=extend_schema(
        summary="Maak een LOCATIE aan.",
    ),
    update=extend_schema(
        summary="Werk een LOCATIE in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een LOCATIE deels bij.",
    ),
    destroy=extend_schema(
        summary="Verwijder een LOCATIE.",
    ),
)
class LocatieViewSet(AuditTrailViewSetMixin, OrderedModelViewSet):
    queryset = Locatie.objects.all()
    serializer_class = LocatieSerializer
    lookup_field = "uuid"
    filterset_class = LocatieFilterSet
