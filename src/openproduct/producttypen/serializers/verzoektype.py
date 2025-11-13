from rest_framework import serializers

from openproduct.producttypen.models import ProductType, VerzoekType
from openproduct.urn.serializers import UrnMappingMixin


class NestedVerzoekTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerzoekType
        fields = ("urn", "url")


class VerzoekTypeSerializer(UrnMappingMixin, serializers.ModelSerializer):
    producttype = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=ProductType.objects.all()
    )

    urn_fields = ["."]

    class Meta:
        model = VerzoekType
        fields = ("producttype", "urn", "url")
        extra_kwargs = {"urn": {"required": False}, "url": {"required": False}}
        validators = []
