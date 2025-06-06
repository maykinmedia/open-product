from django.utils.translation import gettext_lazy as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from vng_api_common.utils import get_help_text

from openproduct.producttypen.models import ProductType, VerzoekType


class NestedVerzoekTypeSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(help_text=_("De url naar het verzoektype."))
    uuid = serializers.UUIDField(
        write_only=True, help_text=get_help_text("producttypen.VerzoekType", "uuid")
    )

    @extend_schema_field(OpenApiTypes.URI)
    def get_url(self, obj):
        return f"{self.context['externe_verwijzing_config'].verzoektypen_url.rstrip('/')}/{obj.uuid}"

    class Meta:
        model = VerzoekType
        fields = ("uuid", "url")


class VerzoekTypeSerializer(serializers.ModelSerializer):
    producttype = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=ProductType.objects.all()
    )

    class Meta:
        model = VerzoekType
        fields = ("uuid", "producttype")
