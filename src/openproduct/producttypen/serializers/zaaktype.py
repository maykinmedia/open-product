from django.utils.translation import gettext_lazy as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from openproduct.producttypen.models import (
    ExterneVerwijzingConfig,
    ProductType,
    ZaakType,
)


class NestedZaakTypeSerializer(serializers.ModelSerializer):

    url = serializers.SerializerMethodField(help_text=_("De url naar het zaaktype."))
    uuid = serializers.UUIDField(
        write_only=True, help_text=_("Uuid naar het zaaktype.")
    )

    @extend_schema_field(OpenApiTypes.URI)
    def get_url(self, obj):
        return f"{obj.zaaktypen_api.basis_url.rstrip('/')}/{obj.uuid}"

    class Meta:
        model = ZaakType
        fields = ("uuid", "url")


class ZaakTypeSerializer(serializers.ModelSerializer):
    producttype = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=ProductType.objects.all()
    )

    basis_url = serializers.SlugRelatedField(
        slug_field="basis_url",
        queryset=ExterneVerwijzingConfig.objects.all(),
        source="zaaktypen_api",
        write_only=True,
        help_text=_("url van een bestaande externe verwijzing config."),
    )

    class Meta:
        model = ZaakType
        fields = ("uuid", "producttype", "basis_url")
