from django.utils.translation import gettext_lazy as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema_field,
    extend_schema_serializer,
)
from rest_framework import serializers
from vng_api_common.utils import get_help_text

from openproduct.producttypen.models import Actie, ProductType
from openproduct.producttypen.models.dmn_config import DmnConfig
from openproduct.producttypen.serializers.validators import ActieUrlValidator
from openproduct.utils.fields import UUIDRelatedField


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "actie response (url)",
            value={
                "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "producttype_uuid": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                "naam": "Parkeervergunning opzegging",
                "url": "https://gemeente-a-forms/46aa6b3a-c0a1-11e6-bc93-6ab56fad108a",
                "mapping": None,
            },
            response_only=True,
        ),
        OpenApiExample(
            "actie response (dmn)",
            value={
                "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "producttype_uuid": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                "naam": "Parkeervergunning opzegging",
                "url": "https://gemeente-a-flowable/dmn-repository/decision-tables/46aa6b3a-c0a1-11e6-bc93-6ab56fad108a",
                "mapping": {
                    "product": [
                        {
                            "name": "pid",
                            "regex": "$.uuid",
                            "classType": "String",
                        },
                        {
                            "name": "geldigheideinddatum",
                            "regex": "$.eindDatum",
                            "classType": "String",
                        },
                        {
                            "name": "aantaluren",
                            "regex": "$.verbruiksobject.uren",
                            "classType": "String",
                        },
                    ],
                    "static": [
                        {
                            "name": "formulieren",
                            "classType": "String",
                            "value": "https://openformulieren-gemeente-a.nl",
                        }
                    ],
                },
            },
            response_only=True,
        ),
        OpenApiExample(
            "actie request (url)",
            value={
                "producttype_uuid": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                "naam": "Parkeervergunning opzegging",
                "direct_url": "https://gemeente-a-forms/46aa6b3a-c0a1-11e6-bc93-6ab56fad108a",
            },
            request_only=True,
        ),
        OpenApiExample(
            "actie request (dmn)",
            value={
                "producttype_uuid": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                "naam": "Parkeervergunning opzegging",
                "tabel_endpoint": "https://gemeente-a-flowable/dmn-repository/decision-tables",
                "dmn_tabel_id": "46aa6b3a-c0a1-11e6-bc93-6ab56fad108a",
                "mapping": {
                    "product": [
                        {
                            "name": "pid",
                            "regex": "$.uuid",
                            "classType": "String",
                        },
                        {
                            "name": "geldigheideinddatum",
                            "regex": "$.eindDatum",
                            "classType": "String",
                        },
                        {
                            "name": "aantaluren",
                            "regex": "$.verbruiksobject.uren",
                            "classType": "String",
                        },
                    ],
                    "static": [
                        {
                            "name": "formulieren",
                            "classType": "String",
                            "value": "https://openformulieren-gemeente-a.nl",
                        }
                    ],
                },
            },
            request_only=True,
        ),
    ],
)
class ActieSerializer(serializers.ModelSerializer):
    producttype_uuid = UUIDRelatedField(
        source="producttype", queryset=ProductType.objects.all()
    )

    tabel_endpoint = serializers.SlugRelatedField(
        slug_field="tabel_endpoint",
        queryset=DmnConfig.objects.all(),
        source="dmn_config",
        write_only=True,
        help_text=_("tabel endpoint van een bestaande dmn config."),
        required=False,
    )

    direct_url = serializers.URLField(
        write_only=True,
        help_text=get_help_text("producttypen.Actie", "direct_url"),
        required=False,
    )

    dmn_tabel_id = serializers.CharField(
        write_only=True,
        help_text=get_help_text("producttypen.Actie", "dmn_tabel_id"),
        required=False,
    )

    url = serializers.SerializerMethodField(help_text=_("De url naar de dmn tabel."))

    @extend_schema_field(OpenApiTypes.URI)
    def get_url(self, obj):
        return obj.url

    class Meta:
        model = Actie
        fields = (
            "uuid",
            "naam",
            "direct_url",
            "tabel_endpoint",
            "dmn_tabel_id",
            "url",
            "producttype_uuid",
            "mapping",
        )
        validators = [ActieUrlValidator()]


class NestedActieSerializer(ActieSerializer):
    class Meta:
        model = Actie
        fields = (
            "uuid",
            "naam",
            "url",
            "mapping",
        )
