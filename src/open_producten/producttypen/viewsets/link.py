import django_filters
from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view

from open_producten.producttypen.models import Link
from open_producten.producttypen.serializers import LinkSerializer
from open_producten.utils.filters import FilterSet
from open_producten.utils.views import OrderedModelViewSet


class LinkFilterSet(FilterSet):
    uniforme_product_naam = django_filters.CharFilter(
        field_name="product_type__uniforme_product_naam__naam", lookup_expr="exact"
    )

    class Meta:
        model = Link
        fields = {
            "product_type__code": ["exact"],
            "product_type__id": ["exact"],
            "naam": ["exact", "contains"],
            "url": ["exact", "contains"],
        }


@extend_schema_view(
    list=extend_schema(
        summary="Alle LINKS opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifieke LINK opvragen.",
    ),
    create=extend_schema(
        summary="Maak een LINK aan.",
        examples=[
            OpenApiExample(
                "Create link",
                value={
                    "product_type_id": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                    "naam": "Open Producten",
                    "url": "https://github.com/maykinmedia/open-producten",
                },
                request_only=True,
            )
        ],
    ),
    update=extend_schema(
        summary="Werk een LINK in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een LINK deels bij.",
    ),
    destroy=extend_schema(
        summary="Verwijder een LINK.",
    ),
)
class LinkViewSet(OrderedModelViewSet):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer
    lookup_url_kwarg = "id"
    filterset_class = LinkFilterSet
