from django.utils.translation import gettext_lazy as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from open_producten.producttypen.models import Proces, ProductType


class NestedProcesSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(help_text=_("De url naar de dmn tabel."))

    @extend_schema_field(OpenApiTypes.URI)
    def get_url(self, obj):
        return obj.url

    class Meta:
        model = Proces
        fields = ("uuid", "url")


class ProcesSerializer(serializers.ModelSerializer):
    product_type = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=ProductType.objects.all()
    )

    class Meta:
        model = Proces
        fields = ("uuid", "product_type")
