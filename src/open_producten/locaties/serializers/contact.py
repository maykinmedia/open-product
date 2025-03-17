from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from open_producten.locaties.models import Contact, Organisatie

from .organisatie import OrganisatieSerializer


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "contact response",
            value={
                "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "organisatie": {
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
                "voornaam": "Bob",
                "achternaam": "de Vries",
                "email": "bob@example.com",
                "telefoonnummer": "0611223344",
                "rol": "medewerker",
            },
            response_only=True,
        ),
        OpenApiExample(
            "contact request",
            value={
                "organisatie_id": "73a745d4-7df0-4510-991e-abfb19f0d861",
                "voornaam": "Bob",
                "achternaam": "de Vries",
                "email": "bob@example.com",
                "telefoonnummer": "0611223344",
                "rol": "medewerker",
            },
            request_only=True,
        ),
    ],
)
class ContactSerializer(serializers.ModelSerializer):
    organisatie = OrganisatieSerializer(read_only=True)
    organisatie_id = serializers.PrimaryKeyRelatedField(
        queryset=Organisatie.objects.all(),
        source="organisatie",
        write_only=True,
        required=False,
    )

    class Meta:
        model = Contact
        fields = "__all__"
