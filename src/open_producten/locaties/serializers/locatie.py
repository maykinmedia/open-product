from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from open_producten.locaties.models import Locatie


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "locatie response",
            value={
                "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "naam": "Maykin Media",
                "email": "info@maykinmedia.nl",
                "telefoonnummer": "+310207530523",
                "straat": "Kingsfortweg",
                "huisnummer": "151",
                "postcode": "1043TESTGR",
                "stad": "Amsterdam",
            },
            response_only=True,
        ),
        OpenApiExample(
            "locatie request",
            value={
                "naam": "Maykin Media",
                "email": "info@maykinmedia.nl",
                "telefoonnummer": "+310207530523",
                "straat": "Kingsfortweg",
                "huisnummer": "151",
                "postcode": "1043 GR",
                "stad": "Amsterdam",
            },
            request_only=True,
        ),
    ],
)
class LocatieSerializer(serializers.ModelSerializer):

    class Meta:
        model = Locatie
        fields = "__all__"
