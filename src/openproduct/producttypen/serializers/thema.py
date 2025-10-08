from django.db import transaction
from django.utils.translation import gettext_lazy as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema_field,
    extend_schema_serializer,
)
from rest_framework import serializers
from vng_api_common.utils import get_help_text

from openproduct.producttypen.models import ProductType, Thema, UniformeProductNaam

from ...utils.drf_validators import DuplicateIdValidator
from ...utils.fields import UUIDRelatedField
from .validators import ThemaGepubliceerdStateValidator, ThemaReferenceValidator


class NestedProductTypeSerializer(serializers.ModelSerializer):
    uniforme_product_naam = serializers.SlugRelatedField(
        slug_field="naam", queryset=UniformeProductNaam.objects.all()
    )

    gepubliceerd = serializers.SerializerMethodField(
        help_text=_("Geeft aan of het producttype getoond kan worden."),
    )

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_gepubliceerd(self, obj):
        return obj.gepubliceerd

    class Meta:
        model = ProductType
        fields = (
            "uuid",
            "code",
            "keywords",
            "uniforme_product_naam",
            "toegestane_statussen",
            "gepubliceerd",
            "publicatie_start_datum",
            "publicatie_eind_datum",
            "aanmaak_datum",
            "update_datum",
        )


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "thema response",
            value={
                "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "naam": "Parkeren",
                "beschrijving": "Parkeren in gemeente ABC",
                "gepubliceerd": True,
                "aanmaak_datum": "2019-08-24T14:15:22Z",
                "update_datum": "2019-08-24T14:15:22Z",
                "hoofd_thema": "41ec14a8-ca7d-43a9-a4a8-46f9587c8d91",
                "producttypen": [
                    {
                        "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                        "code": "129380-C21231",
                        "keywords": ["auto"],
                        "uniforme_product_naam": "parkeervergunning",
                        "toegestane_statussen": ["gereed"],
                        "gepubliceerd": True,
                        "publicatie_start_datum": "2019-09-24",
                        "publicatie_eind_datum": "2030-09-24",
                        "aanmaak_datum": "2019-08-24T14:15:22Z",
                        "update_datum": "2019-08-24T14:15:22Z",
                    }
                ],
            },
            response_only=True,
        ),
        OpenApiExample(
            "thema request",
            value={
                "hoofd_thema": "5f6a2219-5768-4e11-8a8e-ffbafff32482",
                "producttype_uuids": ["95792000-d57f-4d3a-b14c-c4c7aa964907"],
                "gepubliceerd": True,
                "naam": "Parkeren",
                "beschrijving": "Parkeren in gemeente ABC",
            },
            request_only=True,
        ),
    ],
)
class ThemaSerializer(serializers.ModelSerializer):
    hoofd_thema = UUIDRelatedField(
        queryset=Thema.objects.all(),
        allow_null=True,
        help_text=get_help_text("producttypen.Thema", "hoofd_thema"),
    )
    producttypen = NestedProductTypeSerializer(many=True, read_only=True)

    # TODO: remove?
    producttype_uuids = UUIDRelatedField(
        many=True,
        queryset=ProductType.objects.all(),
        write_only=True,
        source="producttypen",
    )

    class Meta:
        model = Thema
        fields = (
            "uuid",
            "naam",
            "beschrijving",
            "gepubliceerd",
            "aanmaak_datum",
            "update_datum",
            "hoofd_thema",
            "producttypen",
            "producttype_uuids",
        )
        validators = [
            DuplicateIdValidator(["producttype_uuids"]),
            ThemaGepubliceerdStateValidator(),
            ThemaReferenceValidator(),
        ]

    @transaction.atomic()
    def create(self, validated_data):
        producttypen = validated_data.pop("producttypen")

        thema = Thema.objects.create(**validated_data)
        thema.producttypen.set(producttypen)

        return thema

    @transaction.atomic()
    def update(self, instance, validated_data):
        producttypen = validated_data.pop("producttypen", None)
        hoofd_thema = validated_data.pop(
            "hoofd_thema", "ignore"
        )  # None is a valid value

        if hoofd_thema != "ignore":
            instance.hoofd_thema = hoofd_thema

        instance = super().update(instance, validated_data)

        if producttypen:
            instance.producttypen.set(producttypen)

        return instance
