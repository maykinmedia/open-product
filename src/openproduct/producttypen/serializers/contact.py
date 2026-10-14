from rest_framework import serializers
from vng_api_common.utils import get_help_text

from openproduct.locaties.models import Contact
from openproduct.locaties.serializers import ContactSerializer

from ...utils.fields import UUIDRelatedField
from ..models import ProductType, ProductTypeContact


class NestedProductTypeContactSerializer(serializers.ModelSerializer):
    contact = ContactSerializer(read_only=True)
    contact_uuid = UUIDRelatedField(
        write_only=True,
        queryset=Contact.objects.all(),
        source="contact",
        help_text=get_help_text("producttypen.ProductTypeContact", "contact"),
    )

    class Meta:
        model = ProductTypeContact
        fields = ("rol", "contact", "contact_uuid")


class ProductTypeContactSerializer(NestedProductTypeContactSerializer):
    producttype = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=ProductType.objects.all()
    )

    class Meta(NestedProductTypeContactSerializer.Meta):
        fields = NestedProductTypeContactSerializer.Meta.fields + ("producttype",)
