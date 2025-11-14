from rest_framework import serializers

from openproduct.producttypen.models import ProductType, ZaakType
from openproduct.urn.serializers import UrnMappingMixin


class NestedZaakTypeSerializer(UrnMappingMixin, serializers.ModelSerializer):


    urn_fields = ["."]
    class Meta:
        model = ZaakType
        fields = ("urn", "url")


class ZaakTypeSerializer(serializers.ModelSerializer):
    producttype = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=ProductType.objects.all()
    )


    class Meta:
        model = ZaakType
        fields = ("producttype", "urn", "url")
        extra_kwargs = {"urn": {"required": False}, "url": {"required": False}}
        validators = []
