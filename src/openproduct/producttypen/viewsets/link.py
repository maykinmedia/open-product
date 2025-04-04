from django.utils.translation import gettext_lazy as _

import django_filters
from drf_spectacular.utils import extend_schema, extend_schema_view

from openproduct.producttypen.models import Link
from openproduct.producttypen.serializers import LinkSerializer
from openproduct.utils.filters import FilterSet, TranslationFilter
from openproduct.utils.views import OrderedModelViewSet


class LinkFilterSet(FilterSet):
    uniforme_product_naam = django_filters.CharFilter(
        field_name="product_type__uniforme_product_naam__naam",
        lookup_expr="exact",
        help_text=_("Uniforme product naam vanuit de UPL."),
    )

    product_type__naam = TranslationFilter(
        field_name="product_type__naam",
        lookup_expr="exact",
        help_text=_("Naam van het product type."),
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
