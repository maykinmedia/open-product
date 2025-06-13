from django.utils.translation import activate

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet

from openproduct.logging.api_tools import AuditTrailViewSetMixin
from openproduct.producttypen.models import ContentElement, ContentLabel
from openproduct.producttypen.serializers.content import (
    ContentElementSerializer,
    ContentElementTranslationSerializer,
    ContentLabelSerializer,
)
from openproduct.utils.views import TranslatableViewSetMixin


@extend_schema_view(
    retrieve=extend_schema(
        summary="Een specifiek CONTENTELEMENT opvragen.",
    ),
    create=extend_schema(
        summary="Maak een CONTENTELEMENT aan.",
    ),
    update=extend_schema(
        summary="Werk een CONTENTELEMENT in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een CONTENTELEMENT deels bij.",
    ),
    destroy=extend_schema(
        summary="Verwijder een CONTENTELEMENT.",
    ),
)
class ContentElementViewSet(
    AuditTrailViewSetMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    TranslatableViewSetMixin,
    GenericViewSet,
):
    queryset = ContentElement.objects.select_related("producttype").prefetch_related(
        "translations", "labels"
    )
    serializer_class = ContentElementSerializer
    lookup_field = "uuid"

    def initial(self, request, *args, **kwargs):
        # passing the translated fields to  the create call will set them for the language in the Accept-Language header.
        # but a POST/PUT/PATCH should only set the required language
        # (other languages can be added in the vertaling viewset action)
        if self.action in ["create", "update", "partial_update"]:
            activate("nl")
        return super().initial(request, *args, **kwargs)

    @extend_schema(
        summary="De vertaling van een content element aanpassen.",
        description="nl kan worden aangepast via het model.",
        parameters=[
            OpenApiParameter(
                name="taal",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
            ),
        ],
    )
    @action(
        detail=True,
        methods=["put"],
        serializer_class=ContentElementTranslationSerializer,
        url_path="vertaling/(?P<taal>[^/.]+)",
    )
    def vertaling(self, request, taal, **kwargs):
        return super().update_vertaling(request, taal, **kwargs)

    @extend_schema(
        summary="De vertaling van een content element verwijderen.",
        description="nl kan niet worden verwijderd.",
        parameters=[
            OpenApiParameter(
                name="taal",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
            ),
        ],
    )
    @vertaling.mapping.delete
    def delete_vertaling(self, request, taal, **kwargs):
        return super().delete_vertaling(request, taal, **kwargs)


@extend_schema_view(
    list=extend_schema(
        summary="Alle CONTENTELEMENTLABELS opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
)
class ContentLabelViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = ContentLabel.objects.all()
    serializer_class = ContentLabelSerializer
    lookup_field = "uuid"
