from rest_framework import serializers
from vng_api_common.utils import get_help_text

from openproduct.locaties.models import Organisatie
from openproduct.locaties.serializers import OrganisatieSerializer

from ...utils.fields import UUIDRelatedField
from ..models import ProductType, ProductTypeOrganisatie


class NestedProductTypeOrganisatieSerializer(serializers.ModelSerializer):
    organisatie = OrganisatieSerializer(read_only=True)
    organisatie_uuid = UUIDRelatedField(
        write_only=True,
        queryset=Organisatie.objects.all(),
        source="organisatie",
        help_text=get_help_text("producttypen.ProductTypeOrganisatie", "organisatie"),
    )

    class Meta:
        model = ProductTypeOrganisatie
        fields = ("rol", "organisatie", "organisatie_uuid")


class ProductTypeOrganisatieSerializer(NestedProductTypeOrganisatieSerializer):
    producttype = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=ProductType.objects.all()
    )

    class Meta(NestedProductTypeOrganisatieSerializer.Meta):
        fields = NestedProductTypeOrganisatieSerializer.Meta.fields + ("producttype",)
