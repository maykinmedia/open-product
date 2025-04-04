from django.db import transaction
from django.utils.translation import gettext_lazy as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema_field,
    extend_schema_serializer,
)
from rest_framework import serializers

from ...utils.drf_validators import NestedObjectsValidator
from ..models import Prijs, PrijsOptie, ProductType
from ..models.dmn_config import DmnConfig
from ..models.prijs import PrijsRegel
from .validators import PrijsOptieRegelValidator


class PrijsOptieSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = PrijsOptie
        fields = ("id", "bedrag", "beschrijving")


class PrijsRegelSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    tabel_endpoint = serializers.SlugRelatedField(
        slug_field="tabel_endpoint",
        queryset=DmnConfig.objects.all(),
        source="dmn_config",
        write_only=True,
        help_text=_("tabel endpoint van een bestaande dmn config."),
    )

    dmn_tabel_id = serializers.CharField(
        write_only=True,
        help_text=_("id van de dmn tabel binnen de dmn instantie."),
    )

    url = serializers.SerializerMethodField(help_text=_("De url naar de dmn tabel."))

    @extend_schema_field(OpenApiTypes.URI)
    def get_url(self, obj):
        return obj.url

    class Meta:
        model = PrijsRegel
        fields = ("id", "url", "beschrijving", "dmn_tabel_id", "tabel_endpoint")


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "prijs met opties response",
            value={
                "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "product_type_id": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                "prijsopties": [
                    {
                        "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
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
                "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "product_type_id": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                "prijsregels": [
                    {
                        "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                        "url": "https://gemeente-a-flowable/dmn-repository/decision-tables/46aa6b3a-c0a1-11e6-bc93-6ab56fad108a",
                        "beschrijving": "base",
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
                "product_type_id": "95792000-d57f-4d3a-b14c-c4c7aa964907",
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
                    },
                ],
                "product_type_id": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                "actief_vanaf": "2024-12-01",
            },
            request_only=True,
        ),
    ],
)
class PrijsSerializer(serializers.ModelSerializer):
    prijsopties = PrijsOptieSerializer(many=True, required=False)
    prijsregels = PrijsRegelSerializer(many=True, required=False)
    product_type_id = serializers.PrimaryKeyRelatedField(
        source="product_type", queryset=ProductType.objects.all()
    )

    class Meta:
        model = Prijs
        fields = ("id", "product_type_id", "prijsopties", "prijsregels", "actief_vanaf")
        validators = [
            PrijsOptieRegelValidator(),
            NestedObjectsValidator("prijsopties", PrijsOptie),
            NestedObjectsValidator("prijsregels", PrijsRegel),
        ]

    @transaction.atomic()
    def create(self, validated_data):
        prijsopties = validated_data.pop("prijsopties", [])
        prijsregels = validated_data.pop("prijsregels", [])
        product_type = validated_data.pop("product_type")

        prijs = Prijs.objects.create(**validated_data, product_type=product_type)

        for optie in prijsopties:
            optie.pop("id", None)
            PrijsOptieSerializer().create(optie | {"prijs": prijs})

        for regel in prijsregels:
            regel.pop("id", None)
            PrijsRegelSerializer().create(regel | {"prijs": prijs})

        return prijs

    @transaction.atomic()
    def update(self, instance, validated_data):
        opties = validated_data.pop("prijsopties", None)
        regels = validated_data.pop("prijsregels", None)
        prijs = super().update(instance, validated_data)

        if opties is not None:
            current_optie_ids = set(prijs.prijsopties.values_list("id", flat=True))
            seen_optie_ids = set()

            for optie in opties:
                optie_id = optie.pop("id", None)
                if optie_id is None:
                    PrijsOptieSerializer().create(optie | {"prijs": prijs})

                else:
                    existing_optie = PrijsOptie.objects.get(id=optie_id)
                    PrijsOptieSerializer(partial=self.partial).update(
                        existing_optie, optie
                    )
                    seen_optie_ids.add(optie_id)

            prijs.prijsopties.filter(
                id__in=(current_optie_ids - seen_optie_ids)
            ).delete()

        if regels is not None:
            current_regel_ids = set(
                prijs.prijsregels.values_list("id", flat=True).distinct()
            )
            seen_regel_ids = set()

            for regel in regels:
                regel_id = regel.pop("id", None)
                if regel_id is None:
                    PrijsRegelSerializer().create(regel | {"prijs": prijs})

                else:
                    existing_regel = PrijsRegel.objects.get(id=regel_id)
                    PrijsRegelSerializer(partial=self.partial).update(
                        existing_regel, regel
                    )
                    seen_regel_ids.add(regel_id)

            prijs.prijsregels.filter(
                id__in=(current_regel_ids - seen_regel_ids)
            ).delete()

        return prijs


class NestedPrijsSerializer(PrijsSerializer):
    class Meta:
        model = Prijs
        fields = ("id", "prijsopties", "actief_vanaf")
