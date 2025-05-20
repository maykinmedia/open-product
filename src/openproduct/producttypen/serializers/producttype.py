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

from openproduct.locaties.models import Contact, Locatie, Organisatie
from openproduct.locaties.serializers import (
    ContactSerializer,
    LocatieSerializer,
    OrganisatieSerializer,
)

from ...utils.drf_validators import DuplicateIdValidator
from ...utils.fields import UUIDRelatedField
from ...utils.serializers import set_nested_serializer, validate_key_value_model_keys
from ..models import JsonSchema, ProductType, Thema, UniformeProductNaam
from ..models.validators import check_externe_verwijzing_config_url
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
    hoofd_thema = UUIDRelatedField(
        queryset=Thema.objects.all(),
        help_text=_("Het hoofd thema waaronder dit thema valt."),
    )

    class Meta:
        model = Thema
        fields = (
            "uuid",
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
            "producttype response",
            value={
                "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "uniforme_product_naam": "parkeervergunning",
                "themas": [
                    {
                        "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
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
                        "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
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
                        "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
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
                        "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                        "organisatie": {
                            "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
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
                        "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                        "prijsopties": [
                            {
                                "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                                "bedrag": "50.99",
                                "beschrijving": "normaal",
                            }
                        ],
                        "actief_vanaf": "2019-08-24",
                    }
                ],
                "links": [
                    {
                        "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                        "naam": "Open Product",
                        "url": "https://github.com/maykinmedia/open-product",
                    }
                ],
                "acties": [
                    {
                        "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                        "naam": "Parkeervergunning opzegging",
                        "url": "https://gemeente-a-flowable/dmn-repository/decision-tables/46aa6b3a-c0a1-11e6-bc93-6ab56fad108a",
                    },
                ],
                "bestanden": [
                    {
                        "uuid": "da0df49a-cd71-4e24-9bae-5be8b01f2c36",
                        "bestand": "https://gemeente.open-product.nl/media/test.txt",
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
            "producttype request",
            value={
                "uniforme_product_naam": "aanleunwoning",
                "thema_uuids": ["497f6eca-6276-4993-bfeb-53cbbbba6f08"],
                "locatie_uuids": ["235de068-a9c5-4eda-b61d-92fd7f09e9dc"],
                "organisatie_uuids": ["2c2694f1-f948-4960-8312-d51c3a0e540f"],
                "contact_uuids": ["6863d699-460d-4c1e-9297-16812d75d8ca"],
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
                "dataobject_schema_naam": "data_schema",
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
    thema_uuids = UUIDRelatedField(
        many=True,
        write_only=True,
        queryset=Thema.objects.all(),
        source="themas",
    )

    locaties = LocatieSerializer(many=True, read_only=True)
    locatie_uuids = UUIDRelatedField(
        many=True,
        write_only=True,
        queryset=Locatie.objects.all(),
        default=[],
        source="locaties",
    )

    organisaties = OrganisatieSerializer(many=True, read_only=True)
    organisatie_uuids = UUIDRelatedField(
        many=True,
        write_only=True,
        queryset=Organisatie.objects.all(),
        default=[],
        source="organisaties",
    )

    contacten = ContactSerializer(many=True, read_only=True)
    contact_uuids = UUIDRelatedField(
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
        required=True, max_length=255, help_text=_("naam van het producttype.")
    )
    samenvatting = serializers.CharField(
        required=True,
        help_text=_("Korte beschrijving van het producttype."),
    )

    taal = serializers.SerializerMethodField(
        read_only=True, help_text=_("De huidige taal van het producttype.")
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
        check_externe_verwijzing_config_url("zaaktypen_url")

        return validate_key_value_model_keys(
            zaaktypen,
            "uuid",
            _("Er bestaat al een zaaktype met de uuid {} voor dit ProductType."),
        )

    def validate_verzoektypen(self, verzoektypen: list[dict]):
        check_externe_verwijzing_config_url("verzoektypen_url")

        return validate_key_value_model_keys(
            verzoektypen,
            "uuid",
            _("Er bestaat al een verzoektype met de uuid {} voor dit ProductType."),
        )

    def validate_processen(self, processen: list[dict]):
        check_externe_verwijzing_config_url("processen_url")

        return validate_key_value_model_keys(
            processen,
            "uuid",
            _("Er bestaat al een proces met de uuid {} voor dit ProductType."),
        )

    class Meta:
        model = ProductType
        fields = [
            "uuid",
            "uniforme_product_naam",
            "themas",
            "thema_uuids",
            "locaties",
            "locatie_uuids",
            "organisaties",
            "organisatie_uuids",
            "contacten",
            "contact_uuids",
            "prijzen",
            "links",
            "acties",
            "bestanden",
            "naam",
            "samenvatting",
            "taal",
            "externe_codes",
            "parameters",
            "verbruiksobject_schema",
            "verbruiksobject_schema_naam",
            "dataobject_schema",
            "dataobject_schema_naam",
            "gepubliceerd",
            "aanmaak_datum",
            "update_datum",
            "code",
            "toegestane_statussen",
            "keywords",
            "interne_opmerkingen",
            "zaaktypen",
            "verzoektypen",
            "processen",
        ]
        validators = [
            DuplicateIdValidator(
                ["thema_uuids", "locatie_uuids", "organisatie_uuids", "contacten_uuids"]
            )
        ]

    def validate_thema_uuids(self, themas: list[Thema]) -> list[Thema]:
        if len(themas) == 0:
            raise serializers.ValidationError(_("Er is minimaal één thema vereist."))
        return themas

    @transaction.atomic()
    def create(self, validated_data):
        themas = validated_data.pop("themas")
        locaties = validated_data.pop("locaties")
        organisaties = validated_data.pop("organisaties")
        contacten = validated_data.pop("contacten")
        externe_codes = validated_data.pop("externe_codes", [])
        parameters = validated_data.pop("parameters", [])
        zaaktypen = validated_data.pop("zaaktypen", [])
        verzoektypen = validated_data.pop("verzoektypen", [])
        processen = validated_data.pop("processen", [])

        producttype = ProductType.objects.create(**validated_data)
        producttype.themas.set(themas)
        producttype.locaties.set(locaties)
        producttype.organisaties.set(organisaties)
        producttype.contacten.set(contacten)

        set_nested_serializer(
            [
                externe_code | {"producttype": producttype.pk}
                for externe_code in externe_codes
            ],
            ExterneCodeSerializer,
        )

        set_nested_serializer(
            [parameter | {"producttype": producttype.pk} for parameter in parameters],
            ParameterSerializer,
        )

        set_nested_serializer(
            [zaaktype | {"producttype": producttype.pk} for zaaktype in zaaktypen],
            ZaakTypeSerializer,
        )

        set_nested_serializer(
            [
                verzoektype | {"producttype": producttype.pk}
                for verzoektype in verzoektypen
            ],
            VerzoekTypeSerializer,
        )

        set_nested_serializer(
            [proces | {"producttype": producttype.pk} for proces in processen],
            ProcesSerializer,
        )

        producttype.add_contact_organisaties()
        return producttype

    @transaction.atomic()
    def update(self, instance, validated_data):
        themas = validated_data.pop("themas", None)
        locaties = validated_data.pop("locaties", None)
        organisaties = validated_data.pop("organisaties", None)
        contacten = validated_data.pop("contacten", None)

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
                    externe_code | {"producttype": instance.pk}
                    for externe_code in externe_codes
                ],
                ExterneCodeSerializer,
            )

        if parameters is not None:
            instance.parameters.all().delete()
            set_nested_serializer(
                [parameter | {"producttype": instance.pk} for parameter in parameters],
                ParameterSerializer,
            )

        if zaaktypen is not None:
            instance.zaaktypen.all().delete()
            set_nested_serializer(
                [zaaktype | {"producttype": instance.pk} for zaaktype in zaaktypen],
                ZaakTypeSerializer,
            )

        if verzoektypen is not None:
            instance.verzoektypen.all().delete()
            set_nested_serializer(
                [
                    verzoektype | {"producttype": instance.pk}
                    for verzoektype in verzoektypen
                ],
                VerzoekTypeSerializer,
            )

        if processen is not None:
            instance.processen.all().delete()
            set_nested_serializer(
                [proces | {"producttype": instance.pk} for proces in processen],
                ProcesSerializer,
            )

        instance.add_contact_organisaties()
        return instance


class ProductTypeActuelePrijsSerializer(serializers.ModelSerializer):
    upl_uri = serializers.ReadOnlyField(source="uniforme_product_naam.uri")
    upl_naam = serializers.ReadOnlyField(source="uniforme_product_naam.naam")
    actuele_prijs = NestedPrijsSerializer(allow_null=True)

    class Meta:
        model = ProductType
        fields = ("uuid", "code", "upl_naam", "upl_uri", "actuele_prijs")


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
            "uuid",
            "naam",
            "samenvatting",
        )
