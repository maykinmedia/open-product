from django.utils.translation import gettext_lazy as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema_field,
    extend_schema_serializer,
)
from parler_rest.serializers import TranslatableModelSerializer
from rest_framework import serializers

from openproduct.producttypen.models import ContentElement, ContentLabel, ProductType


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "content element response",
            value={
                "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "labels": ["openingstijden"],
                "content": "ma-vr 8:00-17:00",
                "taal": "nl",
                "product_type_id": "5f6a2219-5768-4e11-8a8e-ffbafff32482",
            },
            response_only=True,
        ),
        OpenApiExample(
            "content element request",
            value={
                "labels": ["openingstijden"],
                "content": "ma-vr 8:00-17:00",
                "product_type_id": "5f6a2219-5768-4e11-8a8e-ffbafff32482",
            },
            request_only=True,
        ),
    ],
)
class ContentElementSerializer(TranslatableModelSerializer):
    labels = serializers.SlugRelatedField(
        slug_field="naam",
        queryset=ContentLabel.objects.all(),
        many=True,
        required=False,
    )

    content = serializers.CharField(
        required=True,
        max_length=255,
        help_text=_("De content van dit content element."),
    )

    product_type_id = serializers.PrimaryKeyRelatedField(
        source="product_type", queryset=ProductType.objects.all()
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
        fields = ("id", "content", "labels", "product_type_id", "taal")

    def create(self, validated_data):
        content = validated_data.pop("content")

        content_element = super().create(validated_data)
        content_element.set_current_language("nl")
        content_element.content = content

        return content_element

    def update(self, instance, validated_data):
        content = validated_data.pop("content", None)

        instance = super().update(instance, validated_data)

        instance.set_current_language("nl")
        if content:
            instance.content = content

        return instance


class NestedContentElementSerializer(ContentElementSerializer):

    class Meta:
        model = ContentElement
        fields = (
            "id",
            "taal",
            "content",
            "labels",
        )


class ContentElementTranslationSerializer(serializers.ModelSerializer):
    content = serializers.CharField(
        required=True,
        help_text=_("De content van dit content element."),
    )

    class Meta:
        model = ContentElement
        fields = ("id", "content")


class ContentLabelSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContentLabel
        fields = ("naam",)
