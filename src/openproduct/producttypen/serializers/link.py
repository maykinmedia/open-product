from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from openproduct.producttypen.models import Link, ProductType
from openproduct.utils.fields import UUIDRelatedField


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "link response",
            value={
                "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "producttype_uuid": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                "naam": "Open Product",
                "url": "https://github.com/maykinmedia/open-product",
            },
            response_only=True,
        ),
        OpenApiExample(
            "link request",
            value={
                "producttype_uuid": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                "naam": "Open Product",
                "url": "https://github.com/maykinmedia/open-product",
            },
            request_only=True,
        ),
    ],
)
class LinkSerializer(serializers.ModelSerializer):
    producttype_uuid = UUIDRelatedField(
        source="producttype", queryset=ProductType.objects.all()
    )

    class Meta:
        model = Link
        fields = ("uuid", "naam", "url", "producttype_uuid")


class NestedLinkSerializer(LinkSerializer):
    class Meta:
        model = Link
        fields = ("uuid", "naam", "url")
