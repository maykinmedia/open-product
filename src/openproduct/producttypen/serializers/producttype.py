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
from vng_api_common.utils import get_help_text

from openproduct.locaties.models import Locatie
from openproduct.locaties.serializers import LocatieSerializer

from ...utils.drf_validators import DuplicateIdValidator
from ...utils.fields import UUIDRelatedField
from ...utils.serializers import (
    set_nested_serializer,
    validate_key_value_model_keys,
    validate_unique_related,
)
from ..models import (
    FacetWaarde,
    JsonSchema,
    ProductType,
    Thema,
    UniformeProductNaam,
)
from ..models.validators import (
    validate_meervoudige_facetten,
    validate_verplichte_facetten,
)
from . import JsonSchemaSerializer
from .actie import NestedActieSerializer
from .bestand import NestedBestandSerializer
from .contact import NestedProductTypeContactSerializer, ProductTypeContactSerializer
from .externe_code import ExterneCodeSerializer, NestedExterneCodeSerializer
from .facets import ProductTypenFacettenSerializer
from .link import NestedLinkSerializer
from .organisatie import (
    NestedProductTypeOrganisatieSerializer,
    ProductTypeOrganisatieSerializer,
)
from .parameter import NestedParameterSerializer, ParameterSerializer
from .prijs import NestedPrijsSerializer
from .proces import NestedProcesSerializer, ProcesSerializer
from .validators import DoelgroepUplValidator, PublicatieDateValidator
from .verzoektype import NestedVerzoekTypeSerializer, VerzoekTypeSerializer
from .zaaktype import NestedZaakTypeSerializer, ZaakTypeSerializer


class NestedThemaSerializer(serializers.ModelSerializer):
    hoofd_thema = UUIDRelatedField(
        queryset=Thema.objects.all(),
        help_text=get_help_text("producttypen.Thema", "hoofd_thema"),
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
                "doelgroep": "burgers",
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
                        "naam": "Maykin",
                        "email": "info@maykin.nl",
                        "telefoonnummer": "+310207530523",
                        "straat": "Kingsfortweg",
                        "huisnummer": "151",
                        "postcode": "1043 GR",
                        "stad": "Amsterdam",
                    }
                ],
                "organisaties": [
                    {
                        "rol": "leverancier",
                        "organisatie": {
                            "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                            "naam": "Maykin",
                            "code": "ORG-1234",
                            "email": "info@maykin.nl",
                            "telefoonnummer": "+310207530523",
                            "straat": "Kingsfortweg",
                            "huisnummer": "151",
                            "postcode": "1043 GR",
                            "stad": "Amsterdam",
                        },
                    }
                ],
                "facetwaarden": [
                    {
                        "uuid": "66e6e258-ef5f-4859-a774-89ad2756c9ad",
                        "naam": "facetwaarde 1",
                        "omschrijving": "facetwaarde omschrijving",
                        "actief": True,
                        "facet_type": {
                            "uuid": "27e7277f-226d-4345-b61e-e3a96d1b891a",
                            "naam": "facettype 1",
                            "omschrijving": "facet_type omschrijving",
                            "facetteerbaar": False,
                            "meervoudig_toegestaan": False,
                            "verplicht": False,
                        },
                    }
                ],
                "eigenaar": "urn:nld:maykin:openzaak:organisatie:medewerker:uuid:497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "contacten": [
                    {
                        "rol": "relatiemanager",
                        "contact": {
                            "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                            "organisatie": {
                                "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                                "naam": "Maykin",
                                "code": "ORG-1234",
                                "email": "info@maykin.nl",
                                "telefoonnummer": "+310207530523",
                                "straat": "Kingsfortweg",
                                "huisnummer": "151",
                                "postcode": "1043 GR",
                                "stad": "Amsterdam",
                            },
                            "naam": "Bob de Vries",
                            "email": "bob@example.com",
                            "telefoonnummer": "0611223344",
                            "rol": "medewerker",
                        },
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
                        "type": "dmn",
                        "method": "",
                        "url": "https://gemeente-a-flowable/dmn-repository/decision-tables/46aa6b3a-c0a1-11e6-bc93-6ab56fad108a",
                        "mapping": {
                            "product": [
                                {
                                    "name": "pid",
                                    "path": "$.uuid",
                                    "classType": "String",
                                }
                            ],
                            "static": [
                                {
                                    "name": "formulieren",
                                    "classType": "String",
                                    "value": "https://openformulieren-gemeente-a.nl",
                                }
                            ],
                        },
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
                    {"naam": "betalingskenmerk", "waarde": "12345AB"},
                ],
                "zaaktypen": [
                    {
                        "urn": "urn:nld:maykin:openzaak:ztc:zaaktype:uuid:99a8bd4f-4144-4105-9850-e477628852fc",
                        "url": "https://gemeente-a.zgw.nl/zaaktypen/99a8bd4f-4144-4105-9850-e477628852fc",
                    }
                ],
                "verzoektypen": [
                    {
                        "urn": "urn:nld:maykin:openzaak:vtc:verzoektype:uuid:99a8bd4f-4144-4105-9850-e477628852fc",
                        "url": "https://gemeente-a.zgw.nl/verzoektypen/99a8bd4f-4144-4105-9850-e477628852fc",
                    }
                ],
                "processen": [
                    {
                        "urn": "urn:nld:maykin:openzaak:ptc:proces:uuid:99a8bd4f-4144-4105-9850-e477628852fc",
                        "url": "https://gemeente-a.zgw.nl/processen/99a8bd4f-4144-4105-9850-e477628852fc",
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
                "publicatie_start_datum": "2019-09-24",
                "publicatie_eind_datum": "2030-09-24",
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
                "doelgroep": "burgers",
                "thema_uuids": ["497f6eca-6276-4993-bfeb-53cbbbba6f08"],
                "locatie_uuids": ["235de068-a9c5-4eda-b61d-92fd7f09e9dc"],
                "organisaties": [
                    {
                        "rol": "leverancier",
                        "organisatie_uuid": "2c2694f1-f948-4960-8312-d51c3a0e540f",
                    }
                ],
                "facetwaarden_uuids": ["49bd9f8e-239e-49f8-a65d-e1daacad1a72"],
                "eigenaar": "urn:nld:maykin:openzaak:organisatie:medewerker:uuid:497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "contacten": [
                    {
                        "rol": "relatiemanager",
                        "contact_uuid": "6863d699-460d-4c1e-9297-16812d75d8ca",
                    }
                ],
                "publicatie_start_datum": "2019-09-24",
                "publicatie_eind_datum": "2030-09-24",
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
                    {"naam": "betalingskenmerk", "waarde": "12345AB"},
                ],
                "zaaktypen": [
                    {
                        "url": "https://gemeente-a.zgw.nl/zaaktypen/99a8bd4f-4144-4105-9850-e477628852fc"
                    }
                ],
                "verzoektypen": [
                    {
                        "urn": "urn:nld:maykin:openzaak:vtc:verzoektype:uuid:99a8bd4f-4144-4105-9850-e477628852fc",
                    }
                ],
                "processen": [
                    {
                        "urn": "urn:nld:maykin:openzaak:ptc:proces:uuid:99a8bd4f-4144-4105-9850-e477628852fc",
                    }
                ],
                "verbruiksobject_schema_naam": "verbruik_schema",
                "dataobject_schema_naam": "data_schema",
            },
            request_only=True,
        ),
    ],
)
class ProductTypeSerializer(TranslatableModelSerializer):
    uniforme_product_naam = serializers.SlugRelatedField(
        slug_field="naam",
        queryset=UniformeProductNaam.objects.all(),
        required=False,
        allow_null=True,
    )

    themas = NestedThemaSerializer(many=True, read_only=True)
    thema_uuids = UUIDRelatedField(
        many=True,
        write_only=True,
        queryset=Thema.objects.all(),
        source="themas",
    )

    facetwaarden = ProductTypenFacettenSerializer(many=True, read_only=True)
    facetwaarden_uuids = UUIDRelatedField(
        many=True,
        write_only=True,
        queryset=FacetWaarde.objects.all(),
        default=[],
        source="facetwaarden",
    )

    locaties = LocatieSerializer(many=True, read_only=True)
    locatie_uuids = UUIDRelatedField(
        many=True,
        write_only=True,
        queryset=Locatie.objects.all(),
        default=[],
        source="locaties",
    )

    organisaties = NestedProductTypeOrganisatieSerializer(
        many=True,
        default=[],
        source="producttype_organisaties",
        help_text=get_help_text("producttypen.ProductType", "organisaties"),
    )

    contacten = NestedProductTypeContactSerializer(
        many=True,
        default=[],
        source="producttype_contacten",
        help_text=get_help_text("producttypen.ProductType", "contacten"),
    )

    prijzen = NestedPrijsSerializer(many=True, read_only=True)
    links = NestedLinkSerializer(many=True, read_only=True)
    bestanden = NestedBestandSerializer(many=True, read_only=True)
    acties = NestedActieSerializer(many=True, read_only=True)

    verbruiksobject_schema = JsonSchemaSerializer(read_only=True, allow_null=True)
    verbruiksobject_schema_naam = serializers.SlugRelatedField(
        slug_field="naam",
        queryset=JsonSchema.objects.all(),
        write_only=True,
        help_text=get_help_text("producttypen.ProductType", "verbruiksobject_schema"),
        required=False,
        source="verbruiksobject_schema",
    )

    dataobject_schema = JsonSchemaSerializer(read_only=True, allow_null=True)
    dataobject_schema_naam = serializers.SlugRelatedField(
        slug_field="naam",
        queryset=JsonSchema.objects.all(),
        write_only=True,
        help_text=get_help_text("producttypen.ProductType", "dataobject_schema"),
        required=False,
        source="dataobject_schema",
    )

    naam = serializers.CharField(
        required=True,
        max_length=255,
        help_text=get_help_text("producttypen.ProductTypeTranslation", "naam"),
    )
    samenvatting = serializers.CharField(
        required=True,
        help_text=get_help_text("producttypen.ProductTypeTranslation", "samenvatting"),
    )

    taal = serializers.SerializerMethodField(
        read_only=True, help_text=_("De huidige taal van het producttype.")
    )

    gepubliceerd = serializers.SerializerMethodField(
        help_text=_("Geeft aan of het producttype getoond kan worden."),
    )

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_gepubliceerd(self, obj):
        return obj.gepubliceerd

    @extend_schema_field(OpenApiTypes.STR)
    def get_taal(self, obj):
        request = self.context.get("request")
        requested_language = getattr(request, "LANGUAGE_CODE", "nl")
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
        validate_key_value_model_keys(
            zaaktypen,
            "urn",
            _("Er bestaat al een zaaktype met de urn {} voor dit ProductType."),
        )

        validate_key_value_model_keys(
            zaaktypen,
            "url",
            _("Er bestaat al een zaaktype met de url {} voor dit ProductType."),
        )

        return zaaktypen

    def validate_verzoektypen(self, verzoektypen: list[dict]):
        validate_key_value_model_keys(
            verzoektypen,
            "urn",
            _("Er bestaat al een verzoektype met de urn {} voor dit ProductType."),
        )

        validate_key_value_model_keys(
            verzoektypen,
            "url",
            _("Er bestaat al een verzoektype met de url {} voor dit ProductType."),
        )

        return verzoektypen

    def validate_processen(self, processen: list[dict]):
        validate_key_value_model_keys(
            processen,
            "urn",
            _("Er bestaat al een proces met de urn {} voor dit ProductType."),
        )

        validate_key_value_model_keys(
            processen,
            "url",
            _("Er bestaat al een proces met de url {} voor dit ProductType."),
        )

        return processen

    class Meta:
        model = ProductType
        fields = [
            "uuid",
            "uniforme_product_naam",
            "doelgroep",
            "themas",
            "thema_uuids",
            "locaties",
            "locatie_uuids",
            "organisaties",
            "facetwaarden",
            "facetwaarden_uuids",
            "eigenaar",
            "contacten",
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
            "publicatie_start_datum",
            "publicatie_eind_datum",
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
                [
                    "thema_uuids",
                    "locatie_uuids",
                    "facetwaarden_uuids",
                ]
            ),
            PublicatieDateValidator(),
            DoelgroepUplValidator(),
        ]

    def validate_thema_uuids(self, themas: list[Thema]) -> list[Thema]:
        if len(themas) == 0:
            raise serializers.ValidationError(_("Er is minimaal één thema vereist."))
        return themas

    def validate_facetwaarden_uuids(
        self, facetwaarden: list[FacetWaarde]
    ) -> list[FacetWaarde]:
        validate_meervoudige_facetten(facetwaarden)
        validate_verplichte_facetten(facetwaarden)
        return facetwaarden

    def validate_organisaties(self, organisaties: list[dict]) -> list[dict]:
        return validate_unique_related(organisaties, "organisatie")

    def validate_contacten(self, contacten: list[dict]) -> list[dict]:
        return validate_unique_related(contacten, "contact")

    @transaction.atomic()
    def create(self, validated_data):
        organisaties = validated_data.pop("producttype_organisaties", [])
        contacten = validated_data.pop("producttype_contacten", [])
        externe_codes = validated_data.pop("externe_codes", [])
        parameters = validated_data.pop("parameters", [])
        zaaktypen = validated_data.pop("zaaktypen", [])
        verzoektypen = validated_data.pop("verzoektypen", [])
        processen = validated_data.pop("processen", [])

        producttype = super().create(validated_data)

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

        set_nested_serializer(
            [
                {
                    "producttype": producttype.pk,
                    "organisatie_uuid": organisatie["organisatie"].uuid,
                    "rol": organisatie.get("rol", ""),
                }
                for organisatie in organisaties
            ],
            ProductTypeOrganisatieSerializer,
        )

        set_nested_serializer(
            [
                {
                    "producttype": producttype.pk,
                    "contact_uuid": contact["contact"].uuid,
                    "rol": contact.get("rol", ""),
                }
                for contact in contacten
            ],
            ProductTypeContactSerializer,
        )

        return producttype

    @transaction.atomic()
    def update(self, instance, validated_data):
        themas = validated_data.pop("themas", None)
        facetwaarden = validated_data.pop("facetwaarden", None)
        locaties = validated_data.pop("locaties", None)
        organisaties = validated_data.pop("producttype_organisaties", None)
        contacten = validated_data.pop("producttype_contacten", None)

        externe_codes = validated_data.pop("externe_codes", None)
        parameters = validated_data.pop("parameters", None)
        zaaktypen = validated_data.pop("zaaktypen", None)
        verzoektypen = validated_data.pop("verzoektypen", None)
        processen = validated_data.pop("processen", None)

        instance = super().update(instance, validated_data)

        if themas:  # Er is minimaal één thema vereist
            instance.themas.set(themas)
        if facetwaarden is not None:
            instance.facetwaarden.set(facetwaarden)
        if locaties is not None:
            instance.locaties.set(locaties)

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

        if organisaties is not None:
            instance.producttype_organisaties.all().delete()
            set_nested_serializer(
                [
                    {
                        "producttype": instance.pk,
                        "organisatie_uuid": organisatie["organisatie"].uuid,
                        "rol": organisatie.get("rol", ""),
                    }
                    for organisatie in organisaties
                ],
                ProductTypeOrganisatieSerializer,
            )

        if contacten is not None:
            instance.producttype_contacten.all().delete()
            set_nested_serializer(
                [
                    {
                        "producttype": instance.pk,
                        "contact_uuid": contact["contact"].uuid,
                        "rol": contact.get("rol", ""),
                    }
                    for contact in contacten
                ],
                ProductTypeContactSerializer,
            )

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
        required=True,
        max_length=255,
        help_text=get_help_text("producttypen.ProductTypeTranslation", "naam"),
    )
    samenvatting = serializers.CharField(
        required=True,
        help_text=get_help_text("producttypen.ProductTypeTranslation", "samenvatting"),
    )

    class Meta:
        model = ProductType
        fields = (
            "uuid",
            "naam",
            "samenvatting",
        )
