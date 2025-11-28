from rest_framework import serializers

from openproduct.producttypen.models import Proces, ProductType
from openproduct.urn.serializers import UrnMappingMixin


class NestedProcesSerializer(UrnMappingMixin, serializers.ModelSerializer):
    urn_fields = ["."]

    class Meta:
        model = Proces
        fields = ("urn", "url")


class ProcesSerializer(serializers.ModelSerializer):
    producttype = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=ProductType.objects.all()
    )

    class Meta:
        model = Proces
        fields = ("producttype", "urn", "url")
        # because of the unique together constraint in the model, drf makes both fields required, but only one is.
        extra_kwargs = {"urn": {"required": False}, "url": {"required": False}}
        validators = []
