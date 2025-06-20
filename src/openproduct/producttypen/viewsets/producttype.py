from django.utils.translation import activate, gettext_lazy as _

import django_filters
import structlog
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from vng_api_common.utils import get_help_text

from openproduct.logging.api_tools import AuditTrailViewSetMixin
from openproduct.producttypen.models import (
    ContentElement,
    ExterneVerwijzingConfig,
    ProductType,
)
from openproduct.producttypen.models.producttype import ProductStateChoices
from openproduct.producttypen.serializers import (
    ProductTypeActuelePrijsSerializer,
    ProductTypeSerializer,
)
from openproduct.producttypen.serializers.content import NestedContentElementSerializer
from openproduct.producttypen.serializers.producttype import (
    ProductTypeTranslationSerializer,
)
from openproduct.utils.filters import (
    CharArrayFilter,
    ChoiceArrayFilter,
    FilterSet,
    ManyCharFilter,
    TranslationFilter,
    UUIDFInFilter,
)
from openproduct.utils.validators import ManyRegexValidator
from openproduct.utils.views import TranslatableViewSetMixin

logger = structlog.stdlib.get_logger(__name__)


class ProductTypeFilterSet(FilterSet):
    regex = r"^\[([^:\[\]]+):([^:\[\]]+)\]$"  # [key:value] where the key and value cannot contain `[`, `]` or `:`

    externe_code = ManyCharFilter(
        method="filter_by_externe_code",
        validators=[ManyRegexValidator(regex)],
        help_text=_("Producttype codes uit externe omgevingen. [naam:code]"),
    )

    parameter = ManyCharFilter(
        method="filter_by_parameter",
        validators=[ManyRegexValidator(regex)],
        help_text=_("Producttype parameters. [naam:waarde]"),
    )

    uniforme_product_naam = django_filters.CharFilter(
        field_name="uniforme_product_naam__naam",
        help_text=get_help_text("producttypen.UniformeProductNaam", "naam"),
    )

    letter = TranslationFilter(
        field_name="naam",
        lookup_expr="istartswith",
        help_text=_(
            _(
                "Filter op de eerste letter van de naam van het producttype (in de meegegeven `Accept-Language` taal)."
            ),
        ),
    )

    naam = TranslationFilter(
        field_name="naam",
        lookup_expr="exact",
        help_text=get_help_text("producttypen.ProductTypeTranslation", "naam"),
    )

    keywords = CharArrayFilter(
        field_name="keywords",
        lookup_expr="overlap",
        help_text=get_help_text("producttypen.ProductType", "keywords"),
    )

    toegestane_statussen = ChoiceArrayFilter(
        field_name="toegestane_statussen",
        lookup_expr="overlap",
        choices=ProductStateChoices.choices,
        help_text=get_help_text("producttypen.ProductType", "toegestane_statussen"),
    )

    themas__naam__in = CharArrayFilter(
        field_name="themas__naam",
        distinct=True,
        help_text=_("Lijst van thema namen waarop kan worden gezocht."),
    )

    themas__uuid__in = UUIDFInFilter(
        field_name="themas__uuid",
        distinct=True,
        help_text=_("Lijst van thema uuids waarop kan worden gezocht."),
    )

    def filter_by_externe_code(self, queryset, name, value):
        for val in value:
            value_list = val.strip("[]").split(":")
            if len(value_list) != 2:
                raise ParseError(
                    _("Ongeldig format voor externe_code query parameter.")
                )

            naam, code = value_list
            queryset = queryset.filter(
                externe_codes__naam=naam, externe_codes__code=code
            )
        return queryset

    def filter_by_parameter(self, queryset, name, value):
        for val in value:
            value_list = val.strip("[]").split(":")
            if len(value_list) != 2:
                raise ParseError(_("Ongeldig format voor parameter query parameter."))

            naam, waarde = value_list
            queryset = queryset.filter(parameters__naam=naam, parameters__waarde=waarde)
        return queryset

    class Meta:
        model = ProductType
        fields = {
            "code": ["exact"],
            "gepubliceerd": ["exact"],
            "aanmaak_datum": ["exact", "gte", "lte"],
            "update_datum": ["exact", "gte", "lte"],
            "verbruiksobject_schema__naam": ["exact"],
            "zaaktypen__uuid": ["exact"],
            "verzoektypen__uuid": ["exact"],
            "processen__uuid": ["exact"],
            "themas__naam": ["exact"],
            "themas__uuid": ["exact"],
        }


class ContentFilterSet(FilterSet):
    labels = django_filters.BaseInFilter(
        field_name="labels__naam",
        lookup_expr="in",
        help_text=get_help_text("producttypen.ContentElement", "labels"),
        distinct=True,
    )

    exclude_labels = django_filters.BaseInFilter(
        field_name="labels__naam",
        lookup_expr="in",
        exclude=True,
        help_text=get_help_text("producttypen.ContentElement", "labels"),
    )


class Meta:
    model = ContentElement
    fields = ("label", "exclude_labels")


@extend_schema_view(
    list=extend_schema(
        summary="Alle PRODUCTTYPEN opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek PRODUCTTYPE opvragen.",
    ),
    create=extend_schema(
        summary="Maak een PRODUCTTYPE aan.",
    ),
    update=extend_schema(
        summary="Werk een PRODUCTTYPE in zijn geheel bij.",
    ),
    partial_update=extend_schema(
        summary="Werk een PRODUCTTYPE deels bij.",
        description="Als thema_uuids, locatie_uuids, organisatie_uuids of contact_uuids in een patch request wordt meegegeven wordt deze lijst geheel overschreven.",
    ),
    destroy=extend_schema(
        summary="Verwijder een PRODUCTTYPE.",
    ),
)
class ProductTypeViewSet(
    AuditTrailViewSetMixin, TranslatableViewSetMixin, ModelViewSet
):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    lookup_field = "uuid"
    filterset_class = ProductTypeFilterSet

    def initial(self, request, *args, **kwargs):
        # passing the translated fields to  the create call will set them for the language in the Accept-Language header.
        # but a POST/PUT/PATCH should only set the required language
        # (other languages can be added in the vertaling viewset action)
        if self.action in ["create", "update", "partial_update"]:
            activate("nl")
        return super().initial(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        externe_verwijzing_config = ExterneVerwijzingConfig.get_solo()

        if not all(
            (
                externe_verwijzing_config.zaaktypen_url,
                externe_verwijzing_config.verzoektypen_url,
                externe_verwijzing_config.processen_url,
            )
        ):
            logger.warning(
                "een_of_meerdere_urls_niet_geconfigureerd_in_externe_verwijzing_config"
            )

        context["externe_verwijzing_config"] = externe_verwijzing_config
        return context

    @extend_schema(
        summary="De vertaling van een producttype aanpassen.",
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
        methods=["put", "patch"],
        serializer_class=ProductTypeTranslationSerializer,
        url_path="vertaling/(?P<taal>[^/.]+)",
    )
    def vertaling(self, request, taal, **kwargs):
        return super().update_vertaling(request, taal, **kwargs)

    @extend_schema(
        summary="De vertaling van een producttype verwijderen.",
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

    @extend_schema(
        "actuele_prijzen",
        summary="Alle ACTUELE PRIJZEN opvragen.",
        description="Geeft de huidige prijzen van alle PRODUCTTYPEN terug.",
    )
    @action(
        detail=False,
        serializer_class=ProductTypeActuelePrijsSerializer,
        url_path="actuele-prijzen",
    )
    def actuele_prijzen(self, request):
        producttypen = self.get_queryset().all()
        serializer = ProductTypeActuelePrijsSerializer(producttypen, many=True)
        return Response(serializer.data)

    @extend_schema(
        "actuele_prijs",
        summary="De actuele PRIJS van een PRODUCTTYPE opvragen.",
        description="Geeft de huidige prijzen van alle PRODUCTTYPEN terug.",
    )
    @action(
        detail=True,
        serializer_class=ProductTypeActuelePrijsSerializer,
        url_path="actuele-prijs",
    )
    def actuele_prijs(self, request, uuid=None):
        producttype = self.get_object()
        serializer = ProductTypeActuelePrijsSerializer(producttype)
        return Response(serializer.data)

    @extend_schema(
        "content",
        summary="De CONTENT van een PRODUCTTYPE opvragen.",
        description="Geeft de content van een PRODUCTTYPE terug.",
        parameters=[
            OpenApiParameter(
                name="labels",
                type={"type": "array", "items": {"type": "string"}},
                location=OpenApiParameter.QUERY,
                description="Filter content op basis van de labels.",
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
        ],
    )
    @action(
        detail=True,
        serializer_class=NestedContentElementSerializer,
        url_path="content",
    )
    def content(self, request, uuid=None):
        producttype = self.get_object()

        queryset = producttype.content_elementen

        # Apply filtering
        filterset = ContentFilterSet(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
