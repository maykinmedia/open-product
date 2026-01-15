from django.db.models import Prefetch
from django.db.models.deletion import ProtectedError
from django.utils.translation import gettext_lazy as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from openproduct.logging.api_tools import AuditTrailViewSetMixin
from openproduct.producttypen.models import ProductType, Thema
from openproduct.producttypen.serializers import ThemaSerializer
from openproduct.producttypen.serializers.content import NestedContentElementSerializer
from openproduct.producttypen.viewsets.producttype import ContentFilterSet
from openproduct.utils.filters import FilterSet, UUIDFInFilter


class ThemaFilterSet(FilterSet):
    producttypen__uuid__in = UUIDFInFilter(
        field_name="producttypen__uuid",
        lookup_expr="in",
        distinct=True,
        help_text="Filter thema's op basis van een lijst met producttype uuid's.",
    )

    class Meta:
        model = Thema
        fields = {
            "gepubliceerd": ["exact"],
            "naam": ["exact"],
            "hoofd_thema__naam": ["exact"],
            "hoofd_thema__uuid": ["exact"],
            "aanmaak_datum": ["exact", "gte", "lte"],
            "update_datum": ["exact", "gte", "lte"],
            "producttypen__uuid": ["exact"],
        }


@extend_schema_view(
    list=extend_schema(
        summary="Alle THEMA'S opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek THEMA opvragen.",
    ),
    create=extend_schema(
        summary="Maak een THEMA aan.",
    ),
    update=extend_schema(
        summary="Werk een THEMA in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een THEMA deels bij.",
        description="Als producttype_uuids in een patch request wordt meegegeven wordt deze lijst geheel overschreven.",
    ),
    destroy=extend_schema(
        summary="Verwijder een THEMA.",
    ),
)
class ThemaViewSet(AuditTrailViewSetMixin, ModelViewSet):
    queryset = Thema.objects.select_related("hoofd_thema").prefetch_related(
        Prefetch(
            "producttypen", ProductType.objects.select_related("uniforme_product_naam")
        )
    )
    serializer_class = ThemaSerializer
    lookup_field = "uuid"
    filterset_class = ThemaFilterSet

    @extend_schema(
        summary="De CONTENT van een THEMA opvragen.",
        description="Geeft de content van een THEMA terug.",
        parameters=[
            OpenApiParameter(
                name="labels",
                type={"type": "array", "items": {"type": "string"}},
                location=OpenApiParameter.QUERY,
                description="Filter content op basis van labels.",
                required=False,
                explode=False,
            ),
            OpenApiParameter(
                name="exclude_labels",
                type={"type": "array", "items": {"type": "string"}},
                location=OpenApiParameter.QUERY,
                description="Sluit content met bepaalde labels uit.",
                required=False,
                explode=False,
            ),
            OpenApiParameter(
                name="Accept-Language",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                description="Optionele taal (`nl`, `en`).",
            ),
        ],
        responses=NestedContentElementSerializer(many=True),
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="content-elementen",
        serializer_class=NestedContentElementSerializer,
        filterset_class=None,
    )
    def content_elementen(self, request, *args, **kwargs):
        thema = self.get_object()
        queryset = thema.content_elementen.all()

        filterset = ContentFilterSet(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        errors = []
        for producttype in ProductType.objects.filter(themas__in=[instance]):
            if producttype.themas.count() <= 1:
                errors.append(
                    _(
                        "Producttype {} moet aan een minimaal één thema zijn gelinkt."
                    ).format(producttype)
                )

        if errors:
            return Response(
                data={"producttypen": errors}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                data={
                    "sub_themas": [
                        _(
                            "Dit thema kan niet worden verwijderd omdat er gerelateerde sub_themas zijn."
                        )
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
