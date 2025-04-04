from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from openproduct.locaties.models import Organisatie


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "organisatie response",
            value={
                "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "naam": "Maykin Media",
                "code": "org-1234",
                "email": "info@maykinmedia.nl",
                "telefoonnummer": "+310207530523",
                "straat": "Kingsfortweg",
                "huisnummer": "151",
                "postcode": "1043 GR",
                "stad": "Amsterdam",
            },
            response_only=True,
        ),
        OpenApiExample(
            "organisatie request",
            value={
                "naam": "Maykin Media",
                "code": "org-1234",
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
class OrganisatieSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organisatie
        fields = "__all__"
