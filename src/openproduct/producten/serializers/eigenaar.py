from rest_framework import serializers

from openproduct.producten.models import Eigenaar
from openproduct.producten.serializers.validators import (
    EigenaarIdentifierValidator,
    EigenaarVestigingsnummerValidator,
)
from openproduct.utils.serializers import NestedListSerializer


class EigenaarSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(required=False)

    class Meta:
        model = Eigenaar
        fields = ["uuid", "bsn", "kvk_nummer", "vestigingsnummer", "klantnummer"]
        list_serializer_class = NestedListSerializer
        validators = [
            EigenaarIdentifierValidator(),
            EigenaarVestigingsnummerValidator(),
        ]
