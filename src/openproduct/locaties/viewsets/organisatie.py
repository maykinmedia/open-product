from drf_spectacular.utils import extend_schema, extend_schema_view

from openproduct.locaties.models import Organisatie
from openproduct.locaties.serializers import OrganisatieSerializer
from openproduct.logging.api_tools import AuditTrailViewSetMixin
from openproduct.utils.filters import FilterSet
from openproduct.utils.views import OrderedModelViewSet


class OrganisatieFilterSet(FilterSet):

    class Meta:
        model = Organisatie
        fields = {
            "naam": ["iexact"],
            "email": ["iexact"],
            "telefoonnummer": ["contains"],
            "straat": ["iexact"],
            "huisnummer": ["iexact"],
            "postcode": ["exact"],
            "stad": ["exact"],
            "code": ["exact"],
        }


@extend_schema_view(
    list=extend_schema(
        summary="Alle ORGANISATIES opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifieke ORGANISATIE opvragen.",
    ),
    create=extend_schema(
        summary="Maak een ORGANISATIE aan.",
    ),
    update=extend_schema(
        summary="Werk een ORGANISATIE in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een ORGANISATIE deels bij.",
    ),
    destroy=extend_schema(
        summary="Verwijder een ORGANISATIE.",
    ),
)
class OrganisatieViewSet(AuditTrailViewSetMixin, OrderedModelViewSet):
    queryset = Organisatie.objects.all()
    serializer_class = OrganisatieSerializer
    lookup_field = "uuid"
    filterset_class = OrganisatieFilterSet
