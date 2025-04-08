from rest_framework import serializers

from openproduct.producten.models import Eigenaar
from openproduct.producten.serializers.validators import (
    EigenaarIdentifierValidator,
    EigenaarVestigingsnummerValidator,
)


class EigenaarSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(required=False)

    class Meta:
        model = Eigenaar
        fields = ["uuid", "bsn", "kvk_nummer", "vestigingsnummer", "klantnummer"]
        validators = [
            EigenaarIdentifierValidator(),
            EigenaarVestigingsnummerValidator(),
        ]
