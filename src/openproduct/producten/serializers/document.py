from rest_framework import serializers

from openproduct.producten.models import Document, Product
from openproduct.urn.serializers import UrnMappingMixin


class NestedDocumentSerializer(UrnMappingMixin, serializers.ModelSerializer):
    urn_fields = ["."]

    class Meta:
        model = Document
        fields = ("urn", "url")


class DocumentSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Product.objects.all()
    )

    class Meta:
        model = Document
        fields = ("product", "urn", "url")
        # because of the unique together constraint in the model, drf makes both fields required, but only one is.
        extra_kwargs = {"urn": {"required": False}, "url": {"required": False}}
        validators = []
