from django.utils.translation import gettext_lazy as _

import django_filters
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.viewsets import ModelViewSet

from openproduct.logging.api_tools import AuditTrailViewSetMixin
from openproduct.producttypen.models import Link
from openproduct.producttypen.serializers import LinkSerializer
from openproduct.utils.filters import FilterSet, TranslationFilter


class LinkFilterSet(FilterSet):
    uniforme_product_naam = django_filters.CharFilter(
        field_name="producttype__uniforme_product_naam__naam",
        lookup_expr="exact",
        help_text=_("Uniforme product naam vanuit de UPL."),
    )

    producttype__naam = TranslationFilter(
        field_name="producttype__naam",
        lookup_expr="exact",
        help_text=_("Naam van het producttype."),
    )

    class Meta:
        model = Link
        fields = {
            "producttype__code": ["exact"],
            "producttype__uuid": ["exact"],
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
class LinkViewSet(AuditTrailViewSetMixin, ModelViewSet):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer
    lookup_field = "uuid"
    filterset_class = LinkFilterSet
