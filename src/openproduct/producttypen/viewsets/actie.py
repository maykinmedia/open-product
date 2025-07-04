from django.utils.translation import gettext_lazy as _

import django_filters
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.viewsets import ModelViewSet
from vng_api_common.utils import get_help_text

from openproduct.logging.api_tools import AuditTrailViewSetMixin
from openproduct.producttypen.models import Actie
from openproduct.producttypen.serializers.actie import ActieSerializer
from openproduct.utils.filters import FilterSet, TranslationFilter


class ActieFilterSet(FilterSet):
    uniforme_product_naam = django_filters.CharFilter(
        field_name="producttype__uniforme_product_naam__naam",
        lookup_expr="exact",
        help_text=get_help_text("producttypen.UniformeProductNaam", "naam"),
    )

    producttype__naam = TranslationFilter(
        field_name="producttype__naam",
        lookup_expr="exact",
        help_text=_("De Nederlandse naam van het producttype"),
    )

    class Meta:
        model = Actie
        fields = {
            "producttype__code": ["exact"],
            "producttype__uuid": ["exact"],
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
class ActieViewSet(AuditTrailViewSetMixin, ModelViewSet):
    queryset = Actie.objects.select_related("producttype", "dmn_config")
    serializer_class = ActieSerializer
    lookup_field = "uuid"
    filterset_class = ActieFilterSet
