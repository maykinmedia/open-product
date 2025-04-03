from rest_framework import serializers

from openproduct.producttypen.models import Parameter, ProductType


class NestedParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ("naam", "waarde")


class ParameterSerializer(serializers.ModelSerializer):
    product_type = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=ProductType.objects.all()
    )

    class Meta:
        model = Parameter
        fields = ["naam", "waarde", "product_type"]
