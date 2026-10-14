from rest_framework import serializers

from openproduct.producttypen.models import SubType


class SubTypeSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(required=False)

    class Meta:
        model = SubType
        fields = ("uuid", "naam")
