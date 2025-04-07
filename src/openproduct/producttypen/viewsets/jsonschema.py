from drf_spectacular.utils import extend_schema, extend_schema_view

from openproduct.logging.api_tools import AuditTrailViewSetMixin
from openproduct.producttypen.models import JsonSchema
from openproduct.producttypen.serializers import JsonSchemaSerializer
from openproduct.utils.filters import FilterSet
from openproduct.utils.views import OrderedModelViewSet


class JsonSchemaFilterSet(FilterSet):

    class Meta:
        model = JsonSchema
        fields = {"naam": ["exact", "contains"]}


@extend_schema_view(
    list=extend_schema(
        summary="Alle SCHEMA'S opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek SCHEMA opvragen.",
    ),
    create=extend_schema(
        summary="Maak een SCHEMA aan.",
    ),
    update=extend_schema(
        summary="Werk een SCHEMA in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een SCHEMA deels bij.",
    ),
    destroy=extend_schema(
        summary="Verwijder een SCHEMA.",
    ),
)
class JsonSchemaViewSet(AuditTrailViewSetMixin, OrderedModelViewSet):
    queryset = JsonSchema.objects.all()
    serializer_class = JsonSchemaSerializer
    filterset_class = JsonSchemaFilterSet
