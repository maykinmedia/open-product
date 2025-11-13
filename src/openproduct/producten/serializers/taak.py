from rest_framework import serializers

from openproduct.producten.models import Product, Taak
from openproduct.urn.serializers import UrnMappingMixin


class NestedTaakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taak
        fields = ("urn", "url")


class TaakSerializer(UrnMappingMixin, serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Product.objects.all()
    )

    urn_fields = ["."]

    class Meta:
        model = Taak
        fields = ("product", "urn", "url")
        extra_kwargs = {"urn": {"required": False}, "url": {"required": False}}
        validators = []
