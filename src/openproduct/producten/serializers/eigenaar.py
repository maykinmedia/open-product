from rest_framework import serializers

from openproduct.producten.models import Eigenaar
from openproduct.producten.serializers.validators import (
    EigenaarIdentifierValidator,
    EigenaarVestigingsnummerValidator,
)


class EigenaarSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = Eigenaar
        fields = ["id", "bsn", "kvk_nummer", "vestigingsnummer", "klantnummer"]
        validators = [
            EigenaarIdentifierValidator(),
            EigenaarVestigingsnummerValidator(),
        ]
