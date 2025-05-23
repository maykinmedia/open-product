from django.utils.translation import gettext_lazy as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from vng_api_common.utils import get_help_text

from openproduct.producttypen.models import ProductType, ZaakType


class NestedZaakTypeSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(help_text=_("De url naar het zaaktype."))
    uuid = serializers.UUIDField(
        write_only=True, help_text=get_help_text("producttypen.ZaakType", "uuid")
    )

    @extend_schema_field(OpenApiTypes.URI)
    def get_url(self, obj):
        return f"{self.context['externe_verwijzing_config'].zaaktypen_url.rstrip('/')}/{obj.uuid}"

    class Meta:
        model = ZaakType
        fields = ("uuid", "url")


class ZaakTypeSerializer(serializers.ModelSerializer):
    producttype = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=ProductType.objects.all()
    )

    class Meta:
        model = ZaakType
        fields = ("uuid", "producttype")
