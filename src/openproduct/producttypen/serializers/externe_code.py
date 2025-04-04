from rest_framework import serializers

from openproduct.producttypen.models import ExterneCode, ProductType


class NestedExterneCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExterneCode
        fields = ("naam", "code")


class ExterneCodeSerializer(serializers.ModelSerializer):
    producttype = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=ProductType.objects.all()
    )

    class Meta:
        model = ExterneCode
        fields = ["naam", "code", "producttype"]
