from rest_framework import serializers

from openproduct.producttypen.models import SubType
from openproduct.utils.serializers import NestedCreateRequiredFieldsMixin


class SubTypeSerializer(NestedCreateRequiredFieldsMixin, serializers.ModelSerializer):
    uuid = serializers.UUIDField(required=False)

    class Meta:
        model = SubType
        fields = ("uuid", "naam")
