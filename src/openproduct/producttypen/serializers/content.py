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

from openproduct.producttypen.models import (
    ContentElement,
    ContentLabel,
    ProductType,
    Thema,
)
from openproduct.producttypen.serializers.validators import (
    ContentElementProducttypeThemaValidator,
)
from openproduct.utils.fields import UUIDRelatedField


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "content element response (linked to producttype)",
            value={
                "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "labels": ["openingstijden"],
                "content": "ma-vr 8:00-17:00",
                "aanvullende_informatie": "",
                "taal": "nl",
                "producttype_uuid": "5f6a2219-5768-4e11-8a8e-ffbafff32482",
                "thema_uuid": None,
            },
            response_only=True,
        ),
        OpenApiExample(
            "content element response (linked to thema)",
            value={
                "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "labels": ["openingstijden"],
                "content": "ma-vr 8:00-17:00",
                "aanvullende_informatie": "",
                "taal": "nl",
                "producttype_uuid": None,
                "thema_uuid": "41ec14a8-ca7d-43a9-a4a8-46f9587c8d91",
            },
            response_only=True,
        ),
        OpenApiExample(
            "content element request (linked to producttype)",
            value={
                "labels": ["openingstijden"],
                "content": "ma-vr 8:00-17:00",
                "producttype_uuid": "5f6a2219-5768-4e11-8a8e-ffbafff32482",
            },
            request_only=True,
        ),
        OpenApiExample(
            "content element request (linked to thema)",
            value={
                "labels": ["openingstijden"],
                "content": "ma-vr 8:00-17:00",
                "thema_uuid": "41ec14a8-ca7d-43a9-a4a8-46f9587c8d91",
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
        help_text=get_help_text("producttypen.ContentElementTranslation", "content"),
    )

    aanvullende_informatie = serializers.CharField(
        help_text=get_help_text(
            "producttypen.ContentElementTranslation", "aanvullende_informatie"
        ),
        required=False,
    )

    producttype_uuid = UUIDRelatedField(
        source="producttype",
        queryset=ProductType.objects.all(),
        allow_null=True,
        required=False,
    )

    taal = serializers.SerializerMethodField(
        read_only=True, help_text=_("De huidige taal van het content element.")
    )

    thema_uuid = UUIDRelatedField(
        source="thema",
        queryset=Thema.objects.all(),
        allow_null=True,
        required=False,
        help_text=_("Het thema of subthema van dit content element."),
    )

    @extend_schema_field(OpenApiTypes.STR)
    def get_taal(self, obj):
        requested_language = self.context["request"].LANGUAGE_CODE
        return requested_language if obj.has_translation(requested_language) else "nl"

    class Meta:
        model = ContentElement
        fields = (
            "uuid",
            "content",
            "aanvullende_informatie",
            "labels",
            "producttype_uuid",
            "thema_uuid",
            "taal",
        )
        validators = [
            ContentElementProducttypeThemaValidator(),
        ]


class NestedContentElementSerializer(ContentElementSerializer):
    class Meta:
        model = ContentElement
        fields = (
            "uuid",
            "taal",
            "content",
            "aanvullende_informatie",
            "labels",
        )


class ContentElementTranslationSerializer(serializers.ModelSerializer):
    content = serializers.CharField(
        required=True,
        help_text=get_help_text("producttypen.ContentElementTranslation", "content"),
    )

    aanvullende_informatie = serializers.CharField(
        help_text=get_help_text(
            "producttypen.ContentElementTranslation", "aanvullende_informatie"
        ),
        required=False,
    )

    class Meta:
        model = ContentElement
        fields = ("uuid", "content", "aanvullende_informatie")


class ContentLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentLabel
        fields = ("naam",)
