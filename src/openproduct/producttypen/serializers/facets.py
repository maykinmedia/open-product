from django.db import transaction

from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from openproduct.producttypen.models import FacetType, FacetWaarde

from ...utils.drf_validators import NestedObjectsValidator
from .validators import (
    FacetTypeMeervoudigValidator,
    FacetTypeVerplichtValidator,
    FacetWaardenDeleteValidator,
)


class BaseFacetWaardeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacetWaarde
        fields = [
            "uuid",
            "naam",
            "omschrijving",
            "actief",
        ]


class NestedFacetWaardeSerializer(BaseFacetWaardeSerializer):
    uuid = serializers.UUIDField(required=False)


class BaseFacetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacetType
        fields = [
            "uuid",
            "naam",
            "omschrijving",
            "facetteerbaar",
            "meervoudig_toegestaan",
            "verplicht",
        ]


class ProductTypenFacettenSerializer(BaseFacetWaardeSerializer):
    facet_type = BaseFacetTypeSerializer()

    class Meta(BaseFacetWaardeSerializer.Meta):
        fields = BaseFacetWaardeSerializer.Meta.fields + ["facet_type"]


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "facettype response",
            value={
                "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "naam": "doelgroep",
                "omschrijving": "De doelgroep van het producttype",
                "facetteerbaar": True,
                "meervoudig_toegestaan": True,
                "verplicht": False,
                "waarden": [
                    {
                        "uuid": "41ec14a8-ca7d-43a9-a4a8-46f9587c8d91",
                        "naam": "inwoners",
                        "omschrijving": "",
                        "actief": True,
                    }
                ],
            },
            response_only=True,
        ),
        OpenApiExample(
            "facettype request",
            value={
                "naam": "doelgroep",
                "omschrijving": "De doelgroep van het producttype",
                "facetteerbaar": True,
                "meervoudig_toegestaan": True,
                "verplicht": False,
                "waarden": [
                    {"naam": "inwoners", "omschrijving": "", "actief": True},
                    {"naam": "bedrijven", "omschrijving": "", "actief": True},
                ],
            },
            request_only=True,
        ),
    ],
)
class FacetTypeSerializer(BaseFacetTypeSerializer):
    waarden = NestedFacetWaardeSerializer(many=True, required=False)

    class Meta(BaseFacetTypeSerializer.Meta):
        fields = BaseFacetTypeSerializer.Meta.fields + ["waarden"]
        validators = [
            NestedObjectsValidator("waarden", FacetWaarde),
            FacetTypeMeervoudigValidator(),
            FacetTypeVerplichtValidator(),
            FacetWaardenDeleteValidator(),
        ]

    @transaction.atomic()
    def create(self, validated_data):
        waarden = validated_data.pop("waarden", [])

        facet_type = super().create(validated_data)

        for waarde in waarden:
            waarde.pop("uuid", None)
            NestedFacetWaardeSerializer().create(waarde | {"facet_type": facet_type})

        return facet_type

    @transaction.atomic()
    def update(self, instance, validated_data):
        waarden = validated_data.pop("waarden", None)
        facet_type = super().update(instance, validated_data)

        if waarden is not None:
            current_waarde_uuids = set(
                facet_type.waarden.values_list("uuid", flat=True)
            )
            seen_waarde_uuids = set()

            for waarde in waarden:
                waarde_uuid = waarde.pop("uuid", None)
                if waarde_uuid is None:
                    NestedFacetWaardeSerializer().create(
                        waarde | {"facet_type": facet_type}
                    )

                else:
                    existing_waarde = FacetWaarde.objects.get(uuid=waarde_uuid)
                    NestedFacetWaardeSerializer(partial=self.partial).update(
                        existing_waarde, waarde
                    )
                    seen_waarde_uuids.add(waarde_uuid)

            facet_type.waarden.filter(
                uuid__in=(current_waarde_uuids - seen_waarde_uuids)
            ).delete()

        return facet_type
