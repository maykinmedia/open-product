from rest_framework import serializers

from openproduct.producten.models import Document, Product
from openproduct.urn.serializers import UrnMappingMixin


class NestedDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ("urn", "url")


class DocumentSerializer(UrnMappingMixin, serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Product.objects.all()
    )

    urn_fields = ["."]

    class Meta:
        model = Document
        fields = ("product", "urn", "url")
        extra_kwargs = {"urn": {"required": False}}  # TODO
        validators = []
