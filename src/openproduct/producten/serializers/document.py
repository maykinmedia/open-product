from django.utils.translation import gettext_lazy as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from openproduct.producten.models import Document, Product
from openproduct.producttypen.models import ExterneVerwijzingConfig


class NestedDocumentSerializer(serializers.ModelSerializer):

    url = serializers.SerializerMethodField(help_text=_("De url naar het document."))
    uuid = serializers.UUIDField(
        write_only=True, help_text=_("Uuid naar het document.")
    )

    @extend_schema_field(OpenApiTypes.URI)
    def get_url(self, obj):
        return f"{obj.documenten_api.basis_url.rstrip('/')}/{obj.uuid}"

    class Meta:
        model = Document
        fields = ("uuid", "url")


class DocumentSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Product.objects.all()
    )

    basis_url = serializers.SlugRelatedField(
        slug_field="basis_url",
        queryset=ExterneVerwijzingConfig.objects.all(),
        source="documenten_api",
        write_only=True,
        help_text=_("url van een bestaande externe verwijzing config."),
    )

    url = serializers.SerializerMethodField(help_text=_("De url naar het document."))

    @extend_schema_field(OpenApiTypes.URI)
    def get_url(self, obj):
        return f"{obj.documenten_api.basis_url.rstrip('/')}/{obj.uuid}"

    class Meta:
        model = Document
        fields = ("uuid", "product", "basis_url", "url")
