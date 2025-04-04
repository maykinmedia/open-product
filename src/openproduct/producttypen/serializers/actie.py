from django.utils.translation import gettext_lazy as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema_field,
    extend_schema_serializer,
)
from rest_framework import serializers

from openproduct.producttypen.models import Actie, ProductType
from openproduct.producttypen.models.dmn_config import DmnConfig


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "actie response",
            value={
                "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "product_type_id": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                "naam": "Parkeervergunning opzegging",
                "url": "https://gemeente-a-flowable/dmn-repository/decision-tables/46aa6b3a-c0a1-11e6-bc93-6ab56fad108a",
            },
            response_only=True,
        ),
        OpenApiExample(
            "actie request",
            value={
                "product_type_id": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                "naam": "Parkeervergunning opzegging",
                "tabel_endpoint": "https://gemeente-a-flowable/dmn-repository/decision-tables",
                "dmn_tabel_id": "46aa6b3a-c0a1-11e6-bc93-6ab56fad108a",
            },
            request_only=True,
        ),
    ],
)
class ActieSerializer(serializers.ModelSerializer):
    product_type_id = serializers.PrimaryKeyRelatedField(
        source="product_type", queryset=ProductType.objects.all()
    )

    tabel_endpoint = serializers.SlugRelatedField(
        slug_field="tabel_endpoint",
        queryset=DmnConfig.objects.all(),
        source="dmn_config",
        write_only=True,
        help_text=_("tabel endpoint van een bestaande dmn config."),
    )

    dmn_tabel_id = serializers.CharField(
        write_only=True,
        help_text=_("id van de dmn tabel binnen de dmn instantie."),
    )

    url = serializers.SerializerMethodField(help_text=_("De url naar de dmn tabel."))

    @extend_schema_field(OpenApiTypes.URI)
    def get_url(self, obj):
        return obj.url

    class Meta:
        model = Actie
        fields = (
            "id",
            "naam",
            "tabel_endpoint",
            "dmn_tabel_id",
            "url",
            "product_type_id",
        )


class NestedActieSerializer(ActieSerializer):
    class Meta:
        model = Actie
        fields = ("id", "naam", "url")
