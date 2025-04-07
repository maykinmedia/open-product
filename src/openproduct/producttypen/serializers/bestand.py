from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from openproduct.producttypen.models import Bestand, ProductType
from openproduct.utils.fields import UUIDRelatedField


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "bestand response",
            value={
                "uuid": "da0df49a-cd71-4e24-9bae-5be8b01f2c36",
                "bestand": "https://gemeente.open-product.nl/media/test.txt",
                "producttype_uuid": "b035578b-e855-4b72-9f63-7868b8c4b630",
            },
            response_only=True,
        ),
        OpenApiExample(
            "bestand request",
            value={
                "bestand": "test.txt",
                "producttype_uuid": "95792000-d57f-4d3a-b14c-c4c7aa964907",
            },
            media_type="multipart/form-data",
            request_only=True,
        ),
    ],
)
class BestandSerializer(serializers.ModelSerializer):
    producttype_uuid = UUIDRelatedField(
        source="producttype", queryset=ProductType.objects.all()
    )

    class Meta:
        model = Bestand
        fields = ("uuid", "bestand", "producttype_uuid")


class NestedBestandSerializer(BestandSerializer):
    class Meta:
        model = Bestand
        fields = ("uuid", "bestand")
