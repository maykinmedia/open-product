from django.utils.translation import gettext_lazy as _

import django_filters
from drf_spectacular.utils import extend_schema, extend_schema_view

from openproduct.logging.api_tools import AuditTrailViewSetMixin
from openproduct.producttypen.models import Actie
from openproduct.producttypen.serializers.actie import ActieSerializer
from openproduct.utils.filters import FilterSet, TranslationFilter
from openproduct.utils.views import OrderedModelViewSet


class ActieFilterSet(FilterSet):
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
        model = Actie
        fields = {
            "producttype__code": ["exact"],
            "producttype__id": ["exact"],
            "naam": ["exact", "contains"],
            "dmn_tabel_id": ["exact"],
            "dmn_config__naam": ["exact"],
            "dmn_config__tabel_endpoint": ["exact"],
        }


@extend_schema_view(
    list=extend_schema(
        summary="Alle ACTIE opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifieke ACTIE opvragen.",
    ),
    create=extend_schema(
        summary="Maak een ACTIE aan.",
        description="De tabel_endpoint is een verwijzing naar url gedefinieerd in een DMNCONFIG object. "
        "Deze objecten kunnen in de admin worden aangemaakt.",
    ),
    update=extend_schema(
        summary="Werk een ACTIE in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een ACTIE deels bij.",
    ),
    destroy=extend_schema(
        summary="Verwijder een ACTIE.",
    ),
)
class ActieViewSet(AuditTrailViewSetMixin, OrderedModelViewSet):
    queryset = Actie.objects.all()
    serializer_class = ActieSerializer
    lookup_url_kwarg = "id"
    filterset_class = ActieFilterSet
