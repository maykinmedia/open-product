from django.utils.translation import gettext_lazy as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from vng_api_common.utils import get_help_text

from openproduct.producten.models import Product, Taak


class NestedTaakSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(help_text=_("De url naar de taak."))
    uuid = serializers.UUIDField(
        write_only=True, help_text=get_help_text("producten.Taak", "uuid")
    )

    @extend_schema_field(OpenApiTypes.URI)
    def get_url(self, obj):
        return f"{self.context['externe_verwijzing_config'].taken_url.rstrip('/')}/{obj.uuid}"

    class Meta:
        model = Taak
        fields = ("uuid", "url")


class TaakSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Product.objects.all()
    )

    class Meta:
        model = Taak
        fields = ("uuid", "product")
