from django.utils.translation import gettext_lazy as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema_field,
    extend_schema_serializer,
)
from parler_rest.serializers import TranslatableModelSerializer
from rest_framework import serializers
from vng_api_common.utils import get_help_text

from openproduct.producttypen.models import ContentElement, ContentLabel, ProductType
from openproduct.utils.fields import UUIDRelatedField


class ContentLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentLabel
        fields = ("naam", "type")


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "content element response",
            value={
                "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "labels": {"naam": "openingstijden", "type": "extern"},
                "naam": "Openingstijden",
                "content": "ma-vr 8:00-17:00",
                "taal": "nl",
                "producttype_uuid": "5f6a2219-5768-4e11-8a8e-ffbafff32482",
            },
            response_only=True,
        ),
        OpenApiExample(
            "content element request",
            value={
                "labels": {"naam": "openingstijden", "type": "extern"},
                "naam": "Openingstijden",
                "content": "ma-vr 8:00-17:00",
                "producttype_uuid": "5f6a2219-5768-4e11-8a8e-ffbafff32482",
            },
            request_only=True,
        ),
    ],
)
class ContentElementSerializer(TranslatableModelSerializer):
    labels = ContentLabelSerializer(many=True, read_only=True)

    naam = serializers.CharField(
        required=True,
        help_text=get_help_text("producttypen.ContentElementTranslation", "naam"),
    )

    content = serializers.CharField(
        required=True,
        help_text=get_help_text("producttypen.ContentElementTranslation", "content"),
    )

    producttype_uuid = UUIDRelatedField(
        source="producttype", queryset=ProductType.objects.all()
    )

    taal = serializers.SerializerMethodField(
        read_only=True, help_text=_("De huidige taal van het content element.")
    )

    @extend_schema_field(OpenApiTypes.STR)
    def get_taal(self, obj):
        requested_language = self.context["request"].LANGUAGE_CODE
        return requested_language if obj.has_translation(requested_language) else "nl"

    class Meta:
        model = ContentElement
        fields = ("uuid", "naam", "content", "labels", "producttype_uuid", "taal")


class NestedContentElementSerializer(ContentElementSerializer):
    class Meta:
        model = ContentElement
        fields = (
            "uuid",
            "taal",
            "naam",
            "content",
            "labels",
        )


class ContentElementTranslationSerializer(serializers.ModelSerializer):
    naam = serializers.CharField(
        required=True,
        help_text=get_help_text("producttypen.ContentElementTranslation", "naam"),
    )
    content = serializers.CharField(
        required=True,
        help_text=get_help_text("producttypen.ContentElementTranslation", "content"),
    )

    class Meta:
        model = ContentElement
        fields = ("uuid", "naam", "content")
