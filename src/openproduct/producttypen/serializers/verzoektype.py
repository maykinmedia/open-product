from rest_framework import serializers

from openproduct.producttypen.models import ProductType, VerzoekType
from openproduct.urn.serializers import UrnMappingMixin


class NestedVerzoekTypeSerializer(UrnMappingMixin, serializers.ModelSerializer):
    urn_fields = ["."]

    class Meta:
        model = VerzoekType
        fields = ("urn", "url")


class VerzoekTypeSerializer(serializers.ModelSerializer):
    producttype = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=ProductType.objects.all()
    )

    class Meta:
        model = VerzoekType
        fields = ("producttype", "urn", "url")
        # because of the unique together constraint in the model, drf makes both fields required, but only one is.
        extra_kwargs = {"urn": {"required": False}, "url": {"required": False}}
        validators = []
