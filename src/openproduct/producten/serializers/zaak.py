from rest_framework import serializers

from openproduct.producten.models import Product, Zaak
from openproduct.urn.serializers import UrnMappingMixin


class NestedZaakSerializer(UrnMappingMixin, serializers.ModelSerializer):
    urn_fields = ["."]

    class Meta:
        model = Zaak
        fields = ("urn", "url")


class ZaakSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Product.objects.all()
    )

    class Meta:
        model = Zaak
        fields = ("product", "urn", "url")
        extra_kwargs = {"urn": {"required": False}, "url": {"required": False}}
        validators = []
