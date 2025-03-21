from django.utils.translation import gettext_lazy as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from open_producten.producttypen.models import ProductType, ZaakType


class NestedZaakTypeSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        self.base_url = "https://www.zaaktype.nl/"  # TODO
        super().__init__(*args, **kwargs)

    url = serializers.SerializerMethodField(help_text=_("De url naar het zaaktype."))
    uuid = serializers.UUIDField(
        write_only=True, help_text=_("Uuid naar het zaaktype.")
    )

    @extend_schema_field(OpenApiTypes.URI)
    def get_url(self, obj):
        return f"{self.base_url}{obj.uuid}"

    class Meta:
        model = ZaakType
        fields = ("uuid", "url")


class ZaakTypeSerializer(serializers.ModelSerializer):
    product_type = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=ProductType.objects.all()
    )

    class Meta:
        model = ZaakType
        fields = ("uuid", "product_type")
