import django_filters
from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view

from open_producten.producttypen.models import Prijs
from open_producten.producttypen.serializers import PrijsSerializer
from open_producten.utils.views import OrderedModelViewSet
from open_producten.utils.filters import FilterSet

class PrijsFilterSet(FilterSet):
    uniforme_product_naam = django_filters.CharFilter(
        field_name="product_type__uniforme_product_naam__naam", lookup_expr="exact"
    )

    class Meta:
        model = Prijs
        fields = {
            "product_type__id": ["exact"],
            "product_type__code": ["exact"],
            "actief_vanaf": ["exact", "gte", "lte"],
            "prijsopties__bedrag": ["exact", "gte", "lte"],
            "prijsopties__beschrijving": ["exact"],
        }


@extend_schema_view(
    list=extend_schema(
        summary="Alle PRIJZEN opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifieke PRIJS opvragen.",
    ),
    create=extend_schema(
        summary="Maak een PRIJS aan.",
        examples=[
            OpenApiExample(
                "Create prijs",
                description="prijsOptie bedragen kunnen worden ingevuld als een getal of als string met een . of , voor de decimalen",
                value={
                    "prijsopties": [
                        {"bedrag": "50.99", "beschrijving": "normaal"},
                        {"bedrag": "70.99", "beschrijving": "spoed"},
                    ],
                    "product_type_id": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                    "actief_vanaf": "2024-12-01",
                },
                request_only=True,
            )
        ],
    ),
    update=extend_schema(
        summary="Werk een PRIJS in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een PRIJS deels bij.",
        description="Als prijsopties in een patch request wordt meegegeven wordt deze lijst geheel overschreven.",
    ),
    destroy=extend_schema(
        summary="Verwijder een PRIJS.",
    ),
)
class PrijsViewSet(OrderedModelViewSet):
    queryset = Prijs.objects.all()
    serializer_class = PrijsSerializer
    lookup_url_kwarg = "id"
    filterset_class = PrijsFilterSet
