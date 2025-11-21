from django.db import transaction
from django.utils.translation import gettext_lazy as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema_field,
    extend_schema_serializer,
)
from rest_framework import serializers
from vng_api_common.utils import get_help_text

from ...utils.drf_validators import NestedObjectsValidator
from ...utils.fields import UUIDRelatedField
from ..models import Prijs, PrijsOptie, ProductType
from ..models.dmn_config import DmnConfig
from ..models.prijs import PrijsRegel
from .validators import PrijsOptieRegelValidator


class PrijsOptieSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(required=False)

    class Meta:
        model = PrijsOptie
        fields = ("uuid", "bedrag", "beschrijving")


class PrijsRegelSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(required=False)

    tabel_endpoint = serializers.SlugRelatedField(
        slug_field="tabel_endpoint",
        queryset=DmnConfig.objects.all(),
        source="dmn_config",
        write_only=True,
        help_text=_("tabel endpoint van een bestaande dmn config."),
    )

    dmn_tabel_id = serializers.CharField(
        write_only=True,
        help_text=get_help_text("producttypen.PrijsRegel", "dmn_tabel_id"),
    )

    url = serializers.SerializerMethodField(help_text=_("De url naar de dmn tabel."))

    @extend_schema_field(OpenApiTypes.URI)
    def get_url(self, obj):
        return obj.url

    class Meta:
        model = PrijsRegel
        fields = (
            "uuid",
            "url",
            "beschrijving",
            "dmn_tabel_id",
            "tabel_endpoint",
            "mapping",
        )


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "prijs met opties response",
            value={
                "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "producttype_uuid": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                "prijsopties": [
                    {
                        "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                        "bedrag": "50.99",
                        "beschrijving": "normaal",
                    }
                ],
                "actief_vanaf": "2019-08-24",
            },
            response_only=True,
        ),
        OpenApiExample(
            "prijs met regels response",
            value={
                "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "producttype_uuid": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                "prijsregels": [
                    {
                        "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                        "url": "https://gemeente-a-flowable/dmn-repository/decision-tables/46aa6b3a-c0a1-11e6-bc93-6ab56fad108a",
                        "beschrijving": "base",
                        "mapping": {
                            "product": [
                                {
                                    "name": "pid",
                                    "regex": "$.uuid",
                                    "classType": "String",
                                },
                                {
                                    "name": "geldigheideinddatum",
                                    "regex": "$.eindDatum",
                                    "classType": "String",
                                },
                                {
                                    "name": "aantaluren",
                                    "regex": "$.verbruiksobject.uren",
                                    "classType": "String",
                                },
                            ],
                            "static": [
                                {
                                    "name": "formulieren",
                                    "classType": "String",
                                    "value": "https://openformulieren-gemeente-a.nl",
                                }
                            ],
                        },
                    }
                ],
                "actief_vanaf": "2019-08-24",
            },
            response_only=True,
        ),
        OpenApiExample(
            "prijs met opties request",
            description="prijsOptie bedragen kunnen worden ingevuld als een getal of als string met een . of , voor de decimalen",
            value={
                "prijsopties": [
                    {"bedrag": "50.99", "beschrijving": "normaal"},
                    {"bedrag": "70.99", "beschrijving": "spoed"},
                ],
                "producttype_uuid": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                "actief_vanaf": "2024-12-01",
            },
            request_only=True,
        ),
        OpenApiExample(
            "prijs met regels request",
            description="prijsOptie bedragen kunnen worden ingevuld als een getal of als string met een . of , voor de decimalen",
            value={
                "prijsregels": [
                    {
                        "tabel_endpoint": "https://gemeente-a-flowable/dmn-repository/decision-tables",
                        "dmn_tabel_id": "46aa6b3a-c0a1-11e6-bc93-6ab56fad108a",
                        "beschrijving": "base",
                        "mapping": {
                            "product": [
                                {
                                    "name": "pid",
                                    "regex": "$.uuid",
                                    "classType": "String",
                                },
                                {
                                    "name": "geldigheideinddatum",
                                    "regex": "$.eindDatum",
                                    "classType": "String",
                                },
                                {
                                    "name": "aantaluren",
                                    "regex": "$.verbruiksobject.uren",
                                    "classType": "String",
                                },
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
                "producttype_uuid": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                "actief_vanaf": "2024-12-01",
            },
            request_only=True,
        ),
    ],
)
class PrijsSerializer(serializers.ModelSerializer):
    prijsopties = PrijsOptieSerializer(many=True, required=False)
    prijsregels = PrijsRegelSerializer(many=True, required=False)
    producttype_uuid = UUIDRelatedField(
        source="producttype", queryset=ProductType.objects.all()
    )

    class Meta:
        model = Prijs
        fields = (
            "uuid",
            "producttype_uuid",
            "prijsopties",
            "prijsregels",
            "actief_vanaf",
        )
        validators = [
            PrijsOptieRegelValidator(),
            NestedObjectsValidator("prijsopties", PrijsOptie),
            NestedObjectsValidator("prijsregels", PrijsRegel),
        ]

    @transaction.atomic()
    def create(self, validated_data):
        prijsopties = validated_data.pop("prijsopties", [])
        prijsregels = validated_data.pop("prijsregels", [])
        producttype = validated_data.pop("producttype")

        prijs = super().create({**validated_data, "producttype": producttype})

        for optie in prijsopties:
            optie.pop("uuid", None)
            PrijsOptieSerializer().create(optie | {"prijs": prijs})

        for regel in prijsregels:
            regel.pop("uuid", None)
            PrijsRegelSerializer().create(regel | {"prijs": prijs})

        return prijs

    @transaction.atomic()
    def update(self, instance, validated_data):
        opties = validated_data.pop("prijsopties", None)
        regels = validated_data.pop("prijsregels", None)
        prijs = super().update(instance, validated_data)

        if opties is not None:
            current_optie_uuids = set(prijs.prijsopties.values_list("uuid", flat=True))
            seen_optie_uuids = set()

            for optie in opties:
                optie_uuid = optie.pop("uuid", None)
                if optie_uuid is None:
                    PrijsOptieSerializer().create(optie | {"prijs": prijs})

                else:
                    existing_optie = PrijsOptie.objects.get(uuid=optie_uuid)
                    PrijsOptieSerializer(partial=self.partial).update(
                        existing_optie, optie
                    )
                    seen_optie_uuids.add(optie_uuid)

            prijs.prijsopties.filter(
                uuid__in=(current_optie_uuids - seen_optie_uuids)
            ).delete()

        if regels is not None:
            current_regel_uuids = set(
                prijs.prijsregels.values_list("uuid", flat=True).distinct()
            )
            seen_regel_uuids = set()

            for regel in regels:
                regel_uuid = regel.pop("uuid", None)
                if regel_uuid is None:
                    PrijsRegelSerializer().create(regel | {"prijs": prijs})

                else:
                    existing_regel = PrijsRegel.objects.get(uuid=regel_uuid)
                    PrijsRegelSerializer(partial=self.partial).update(
                        existing_regel, regel
                    )
                    seen_regel_uuids.add(regel_uuid)

            prijs.prijsregels.filter(
                uuid__in=(current_regel_uuids - seen_regel_uuids)
            ).delete()

        return prijs


class NestedPrijsSerializer(PrijsSerializer):
    class Meta:
        model = Prijs
        fields = ("uuid", "prijsopties", "prijsregels", "actief_vanaf")
