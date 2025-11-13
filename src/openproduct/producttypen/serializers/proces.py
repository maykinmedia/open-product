from rest_framework import serializers

from openproduct.producttypen.models import Proces, ProductType
from openproduct.urn.serializers import UrnMappingMixin


class NestedProcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proces
        fields = ("urn", "url")


class ProcesSerializer(UrnMappingMixin, serializers.ModelSerializer):
    producttype = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=ProductType.objects.all()
    )

    urn_fields = ["."]

    class Meta:
        model = Proces
        fields = ("producttype", "urn", "url")
        extra_kwargs = {"urn": {"required": False}, "url": {"required": False}}
        validators = []
