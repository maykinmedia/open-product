from rest_framework import serializers

from openproduct.producttypen.models import FacetType, FacetWaarde

from ...utils.fields import UUIDRelatedField


class BaseFacetWaardeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacetWaarde
        fields = [
            "uuid",
            "naam",
            "omschrijving",
            "actief",
        ]


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


class FacetTypeSerializer(BaseFacetTypeSerializer):
    facetten_waarden = BaseFacetWaardeSerializer(
        many=True, read_only=True, source="waarden"
    )
    facetten_waarden_uuids = UUIDRelatedField(
        many=True,
        write_only=True,
        queryset=FacetWaarde.objects.all(),
        default=list,
        source="waarden",
    )

    class Meta(BaseFacetTypeSerializer.Meta):
        fields = BaseFacetTypeSerializer.Meta.fields + [
            "facetten_waarden",
            "facetten_waarden_uuids",
        ]
