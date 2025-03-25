from django.db import transaction
from django.utils.translation import gettext_lazy as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema_field,
    extend_schema_serializer,
)
from parler_rest.serializers import TranslatableModelSerializer
from rest_framework import serializers

from open_producten.locaties.models import Contact, Locatie, Organisatie
from open_producten.locaties.serializers import (
    ContactSerializer,
    LocatieSerializer,
    OrganisatieSerializer,
)

from ...utils.drf_validators import DuplicateIdValidator
from ...utils.serializers import set_nested_serializer, validate_key_value_model_keys
from ..models import JsonSchema, ProductType, Thema, UniformeProductNaam
from ..models.proces import check_processen_url
from ..models.verzoektype import check_verzoektypen_url
from ..models.zaaktype import check_zaaktypen_url
from . import JsonSchemaSerializer
from .actie import NestedActieSerializer
from .bestand import NestedBestandSerializer
from .externe_code import ExterneCodeSerializer, NestedExterneCodeSerializer
from .link import NestedLinkSerializer
from .parameter import NestedParameterSerializer, ParameterSerializer
from .prijs import NestedPrijsSerializer
from .proces import NestedProcesSerializer, ProcesSerializer
from .verzoektype import NestedVerzoekTypeSerializer, VerzoekTypeSerializer
from .zaaktype import NestedZaakTypeSerializer, ZaakTypeSerializer


class NestedThemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thema
        fields = (
            "id",
            "naam",
            "beschrijving",
            "gepubliceerd",
            "aanmaak_datum",
            "update_datum",
            "hoofd_thema",
        )


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "product type response",
            value={
                "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "uniforme_product_naam": "parkeervergunning",
                "themas": [
                    {
                        "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                        "naam": "Parkeren",
                        "beschrijving": ".....",
                        "gepubliceerd": True,
                        "aanmaak_datum": "2019-08-24T14:15:22Z",
                        "update_datum": "2019-08-24T14:15:22Z",
                        "hoofd_thema": "41ec14a8-ca7d-43a9-a4a8-46f9587c8d91",
                    }
                ],
                "locaties": [
                    {
                        "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                        "naam": "Maykin Media",
                        "email": "info@maykinmedia.nl",
                        "telefoonnummer": "+310207530523",
                        "straat": "Kingsfortweg",
                        "huisnummer": "151",
                        "postcode": "1043 GR",
                        "stad": "Amsterdam",
                    }
                ],
                "organisaties": [
                    {
                        "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                        "naam": "Maykin Media",
                        "code": "org-1234",
                        "email": "info@maykinmedia.nl",
                        "telefoonnummer": "+310207530523",
                        "straat": "Kingsfortweg",
                        "huisnummer": "151",
                        "postcode": "1043 GR",
                        "stad": "Amsterdam",
                    }
                ],
                "contacten": [
                    {
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
                    }
                ],
                "prijzen": [
                    {
                        "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                        "prijsopties": [
                            {
                                "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                                "bedrag": "50.99",
                                "beschrijving": "normaal",
                            }
                        ],
                        "actief_vanaf": "2019-08-24",
                    }
                ],
                "links": [
                    {
                        "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                        "naam": "Open Producten",
                        "url": "https://github.com/maykinmedia/open-producten",
                    }
                ],
                "acties": [
                    {
                        "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                        "naam": "Parkeervergunning opzegging",
                        "url": "https://gemeente-a-flowable/dmn-repository/decision-tables/46aa6b3a-c0a1-11e6-bc93-6ab56fad108a",
                    },
                ],
                "bestanden": [
                    {
                        "id": "da0df49a-cd71-4e24-9bae-5be8b01f2c36",
                        "bestand": "https://gemeente.open-producten.nl/media/test.txt",
                    }
                ],
                "naam": "Parkeervergunning",
                "samenvatting": "korte samenvatting...",
                "taal": "nl",
                "externe_codes": [
                    {"naam": "ISO", "code": "123"},
                    {"naam": "CBS", "code": "456"},
                ],
                "parameters": [
                    {"naam": "doelgroep", "waarde": "inwoners"},
                ],
                "zaaktypen": [
                    {
                        "url": "https://gemeente-a.zgw.nl/zaaktypen/99a8bd4f-4144-4105-9850-e477628852fc"
                    }
                ],
                "verzoektypen": [
                    {
                        "url": "https://gemeente-a.zgw.nl/verzoektypen/99a8bd4f-4144-4105-9850-e477628852fc"
                    }
                ],
                "processen": [
                    {
                        "url": "https://gemeente-a.zgw.nl/processen/99a8bd4f-4144-4105-9850-e477628852fc"
                    }
                ],
                "verbruiksobject_schema": {
                    "naam": "verbruik_schema",
                    "schema": {
                        "type": "object",
                        "properties": {"uren": {"type": "number"}},
                        "required": ["uren"],
                    },
                },
                "dataobject_schema": {
                    "naam": "data_schema",
                    "schema": {
                        "type": "object",
                        "properties": {"max_uren": {"type": "number"}},
                        "required": ["max_uren"],
                    },
                },
                "gepubliceerd": True,
                "aanmaak_datum": "2019-08-24T14:15:22Z",
                "update_datum": "2019-08-24T14:15:22Z",
                "code": "PT-12345",
                "toegestane_statussen": ["gereed"],
                "keywords": ["auto"],
                "interne_opmerkingen": "interne opmerkingen...",
            },
            response_only=True,
        ),
        OpenApiExample(
            "product type request",
            value={
                "uniforme_product_naam": "aanleunwoning",
                "thema_ids": ["497f6eca-6276-4993-bfeb-53cbbbba6f08"],
                "locatie_ids": ["235de068-a9c5-4eda-b61d-92fd7f09e9dc"],
                "organisatie_ids": ["2c2694f1-f948-4960-8312-d51c3a0e540f"],
                "contact_ids": ["6863d699-460d-4c1e-9297-16812d75d8ca"],
                "gepubliceerd": False,
                "naam": "Aanleunwoning",
                "code": "PT-12345",
                "toegestane_statussen": ["gereed", "actief"],
                "interne_opmerkingen": "interne opmerkingen...",
                "samenvatting": "korte samenvatting...",
                "keywords": ["wonen"],
                "externe_codes": [
                    {"naam": "ISO", "code": "123"},
                    {"naam": "CBS", "code": "456"},
                ],
                "parameters": [
                    {"naam": "doelgroep", "waarde": "inwoners"},
                ],
                "zaaktypen": [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}],
                "verzoektypen": [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}],
                "processen": [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}],
                "verbruiksobject_schema_naam": "verbruik_schema",
                "dataobject_schema": "data_schema",
            },
            request_only=True,
        ),
    ],
)
class ProductTypeSerializer(TranslatableModelSerializer):
    uniforme_product_naam = serializers.SlugRelatedField(
        slug_field="naam", queryset=UniformeProductNaam.objects.all()
    )

    themas = NestedThemaSerializer(many=True, read_only=True)
    thema_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Thema.objects.all(),
        source="themas",
    )

    locaties = LocatieSerializer(many=True, read_only=True)
    locatie_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Locatie.objects.all(),
        default=[],
        source="locaties",
    )

    organisaties = OrganisatieSerializer(many=True, read_only=True)
    organisatie_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Organisatie.objects.all(),
        default=[],
        source="organisaties",
    )

    contacten = ContactSerializer(many=True, read_only=True)
    contact_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Contact.objects.all(),
        default=[],
        source="contacten",
    )

    prijzen = NestedPrijsSerializer(many=True, read_only=True)
    links = NestedLinkSerializer(many=True, read_only=True)
    bestanden = NestedBestandSerializer(many=True, read_only=True)
    acties = NestedActieSerializer(many=True, read_only=True)

    verbruiksobject_schema = JsonSchemaSerializer(read_only=True)
    verbruiksobject_schema_naam = serializers.SlugRelatedField(
        slug_field="naam",
        queryset=JsonSchema.objects.all(),
        write_only=True,
        help_text=_(
            "JSON schema om het verbruiksobject van een gerelateerd product te valideren."
        ),
        required=False,
        source="verbruiksobject_schema",
    )

    dataobject_schema = JsonSchemaSerializer(read_only=True)
    dataobject_schema_naam = serializers.SlugRelatedField(
        slug_field="naam",
        queryset=JsonSchema.objects.all(),
        write_only=True,
        help_text=_(
            "JSON schema om het dataobject van een gerelateerd product te valideren."
        ),
        required=False,
        source="dataobject_schema",
    )

    naam = serializers.CharField(
        required=True, max_length=255, help_text=_("naam van het product type.")
    )
    samenvatting = serializers.CharField(
        required=True,
        help_text=_("Korte beschrijving van het product type."),
    )

    taal = serializers.SerializerMethodField(
        read_only=True, help_text=_("De huidige taal van het product type.")
    )

    @extend_schema_field(OpenApiTypes.STR)
    def get_taal(self, obj):
        requested_language = self.context["request"].LANGUAGE_CODE
        return requested_language if obj.has_translation(requested_language) else "nl"

    externe_codes = NestedExterneCodeSerializer(many=True, required=False)
    parameters = NestedParameterSerializer(many=True, required=False)
    zaaktypen = NestedZaakTypeSerializer(many=True, required=False)
    verzoektypen = NestedVerzoekTypeSerializer(many=True, required=False)
    processen = NestedProcesSerializer(many=True, required=False)

    def validate_externe_codes(self, externe_codes: list[dict]):
        return validate_key_value_model_keys(
            externe_codes,
            "naam",
            _("Er bestaat al een externe code met de naam {} voor dit ProductType."),
        )

    def validate_parameters(self, parameters: list[dict]):
        return validate_key_value_model_keys(
            parameters,
            "naam",
            _("Er bestaat al een parameter met de naam {} voor dit ProductType."),
        )

    def validate_zaaktypen(self, zaaktypen: list[dict]):
        check_zaaktypen_url()

        return validate_key_value_model_keys(
            zaaktypen,
            "uuid",
            _("Er bestaat al een zaaktype met de uuid {} voor dit ProductType."),
        )

    def validate_verzoektypen(self, verzoektypen: list[dict]):
        check_verzoektypen_url()

        return validate_key_value_model_keys(
            verzoektypen,
            "uuid",
            _("Er bestaat al een verzoektype met de uuid {} voor dit ProductType."),
        )

    def validate_processen(self, processen: list[dict]):
        check_processen_url()

        return validate_key_value_model_keys(
            processen,
            "uuid",
            _("Er bestaat al een proces met de uuid {} voor dit ProductType."),
        )

    class Meta:
        model = ProductType
        fields = "__all__"
        validators = [
            DuplicateIdValidator(
                ["thema_ids", "locatie_ids", "organisatie_ids", "contacten_ids"]
            )
        ]

    def validate_thema_ids(self, themas: list[Thema]) -> list[Thema]:
        if len(themas) == 0:
            raise serializers.ValidationError(_("Er is minimaal één thema vereist."))
        return themas

    @transaction.atomic()
    def create(self, validated_data):
        themas = validated_data.pop("themas")
        locaties = validated_data.pop("locaties")
        organisaties = validated_data.pop("organisaties")
        contacten = validated_data.pop("contacten")
        naam = validated_data.pop("naam")
        samenvatting = validated_data.pop("samenvatting")
        externe_codes = validated_data.pop("externe_codes", [])
        parameters = validated_data.pop("parameters", [])
        zaaktypen = validated_data.pop("zaaktypen", [])
        verzoektypen = validated_data.pop("verzoektypen", [])
        processen = validated_data.pop("processen", [])

        product_type = ProductType.objects.create(**validated_data)
        product_type.themas.set(themas)
        product_type.locaties.set(locaties)
        product_type.organisaties.set(organisaties)
        product_type.contacten.set(contacten)

        set_nested_serializer(
            [
                externe_code | {"product_type": product_type.id}
                for externe_code in externe_codes
            ],
            ExterneCodeSerializer,
        )

        set_nested_serializer(
            [parameter | {"product_type": product_type.id} for parameter in parameters],
            ParameterSerializer,
        )

        set_nested_serializer(
            [zaaktype | {"product_type": product_type.id} for zaaktype in zaaktypen],
            ZaakTypeSerializer,
        )

        set_nested_serializer(
            [
                verzoektype | {"product_type": product_type.id}
                for verzoektype in verzoektypen
            ],
            VerzoekTypeSerializer,
        )

        set_nested_serializer(
            [proces | {"product_type": product_type.id} for proces in processen],
            ProcesSerializer,
        )

        product_type.set_current_language("nl")
        product_type.naam = naam
        product_type.samenvatting = samenvatting

        product_type.add_contact_organisaties()
        return product_type

    @transaction.atomic()
    def update(self, instance, validated_data):
        themas = validated_data.pop("themas", None)
        locaties = validated_data.pop("locaties", None)
        organisaties = validated_data.pop("organisaties", None)
        contacten = validated_data.pop("contacten", None)

        naam = validated_data.pop("naam", None)
        samenvatting = validated_data.pop("samenvatting", None)
        externe_codes = validated_data.pop("externe_codes", None)
        parameters = validated_data.pop("parameters", None)
        zaaktypen = validated_data.pop("zaaktypen", None)
        verzoektypen = validated_data.pop("verzoektypen", None)
        processen = validated_data.pop("processen", None)

        instance = super().update(instance, validated_data)

        if themas:
            instance.themas.set(themas)
        if locaties:
            instance.locaties.set(locaties)
        if organisaties:
            instance.organisaties.set(organisaties)
        if contacten:
            instance.contacten.set(contacten)

        if externe_codes is not None:
            instance.externe_codes.all().delete()
            set_nested_serializer(
                [
                    externe_code | {"product_type": instance.id}
                    for externe_code in externe_codes
                ],
                ExterneCodeSerializer,
            )

        if parameters is not None:
            instance.parameters.all().delete()
            set_nested_serializer(
                [parameter | {"product_type": instance.id} for parameter in parameters],
                ParameterSerializer,
            )

        if zaaktypen is not None:
            instance.zaaktypen.all().delete()
            set_nested_serializer(
                [zaaktype | {"product_type": instance.id} for zaaktype in zaaktypen],
                ZaakTypeSerializer,
            )

        if verzoektypen is not None:
            instance.verzoektypen.all().delete()
            set_nested_serializer(
                [
                    verzoektype | {"product_type": instance.id}
                    for verzoektype in verzoektypen
                ],
                VerzoekTypeSerializer,
            )

        if processen is not None:
            instance.processen.all().delete()
            set_nested_serializer(
                [proces | {"product_type": instance.id} for proces in processen],
                ProcesSerializer,
            )

        instance.set_current_language("nl")
        if naam:
            instance.naam = naam
        if samenvatting:
            instance.samenvatting = samenvatting

        instance.add_contact_organisaties()
        return instance


class ProductTypeActuelePrijsSerializer(serializers.ModelSerializer):
    upl_uri = serializers.ReadOnlyField(source="uniforme_product_naam.uri")
    upl_naam = serializers.ReadOnlyField(source="uniforme_product_naam.naam")
    actuele_prijs = NestedPrijsSerializer(allow_null=True)

    class Meta:
        model = ProductType
        fields = ("id", "code", "upl_naam", "upl_uri", "actuele_prijs")


class ProductTypeTranslationSerializer(serializers.ModelSerializer):

    naam = serializers.CharField(
        required=True, max_length=255, help_text=_("naam van het producttype.")
    )
    samenvatting = serializers.CharField(
        required=True,
        help_text=_("Korte beschrijving van het producttype."),
    )

    class Meta:
        model = ProductType
        fields = (
            "id",
            "naam",
            "samenvatting",
        )
