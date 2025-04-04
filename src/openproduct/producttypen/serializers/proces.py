from django.utils.translation import gettext_lazy as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from openproduct.producttypen.models import Proces, ProductType


class NestedProcesSerializer(serializers.ModelSerializer):

    url = serializers.SerializerMethodField(help_text=_("De url naar het proces."))
    uuid = serializers.UUIDField(write_only=True, help_text=_("Uuid naar het proces."))

    @extend_schema_field(OpenApiTypes.URI)
    def get_url(self, obj):
        return f"{self.context['externe_verwijzing_config'].processen_url.rstrip('/')}/{obj.uuid}"

    class Meta:
        model = Proces
        fields = ("uuid", "url")


class ProcesSerializer(serializers.ModelSerializer):
    producttype = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=ProductType.objects.all()
    )

    class Meta:
        model = Proces
        fields = ("uuid", "producttype")
