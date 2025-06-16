from django.db import transaction
from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from openproduct.producten.models import Eigenaar, Product
from openproduct.producten.serializers.document import (
    DocumentSerializer,
    NestedDocumentSerializer,
)
from openproduct.producten.serializers.eigenaar import EigenaarSerializer
from openproduct.producten.serializers.taak import NestedTaakSerializer, TaakSerializer
from openproduct.producten.serializers.validators import (
    DataObjectValidator,
    DateValidator,
    StatusValidator,
    VerbruiksObjectValidator,
)
from openproduct.producten.serializers.zaak import NestedZaakSerializer, ZaakSerializer
from openproduct.producttypen.models import ProductType, UniformeProductNaam
from openproduct.producttypen.models.validators import (
    check_externe_verwijzing_config_url,
)
from openproduct.producttypen.serializers.producttype import NestedThemaSerializer
from openproduct.utils.drf_validators import NestedObjectsValidator
from openproduct.utils.fields import UUIDRelatedField
from openproduct.utils.serializers import (
    set_nested_serializer,
    validate_key_value_model_keys,
)


class NestedProductTypeSerializer(serializers.ModelSerializer):
    uniforme_product_naam = serializers.SlugRelatedField(
        slug_field="naam", queryset=UniformeProductNaam.objects.all()
    )

    themas = NestedThemaSerializer(many=True)

    class Meta:
        model = ProductType
        fields = (
            "uuid",
            "code",
            "keywords",
            "uniforme_product_naam",
            "toegestane_statussen",
            "gepubliceerd",
            "aanmaak_datum",
            "update_datum",
            "themas",
        )


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "product response",
            value={
                "uuid": "da0df49a-cd71-4e24-9bae-5be8b01f2c36",
                "url": "https://gemeente.open-product.nl/producten/api/v0/producten/da0df49a-cd71-4e24-9bae-5be8b01f2c36",
                "naam": "verhuurvergunning: straatweg 14",
                "start_datum": "2024-12-01",
                "eind_datum": "2026-12-01",
                "aanmaak_datum": "2019-08-24T14:15:22Z",
                "update_datum": "2019-08-24T14:15:22Z",
                "producttype": {
                    "uuid": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                    "code": "129380-A21231",
                    "keywords": ["auto"],
                    "uniforme_product_naam": "parkeervergunning",
                    "toegestane_statussen": ["gereed"],
                    "gepubliceerd": True,
                    "aanmaak_datum": "2019-08-24T14:15:22Z",
                    "update_datum": "2019-08-24T14:15:22Z",
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
                },
                "gepubliceerd": False,
                "eigenaren": [
                    {
                        "uuid": "9de01697-7fc5-4113-803c-a8c9a8dad4f2",
                        "bsn": "111222333",
                    }
                ],
                "documenten": [
                    {
                        "url": "https://gemeente-a.zgw.nl/documenten/99a8bd4f-4144-4105-9850-e477628852fc"
                    }
                ],
                "zaken": [
                    {
                        "url": "https://gemeente-a.zgw.nl/zaken/eb188bea-51f2-44f0-8acc-eec1c710b4bf"
                    }
                ],
                "taken": [
                    {
                        "url": "https://gemeente-a.zgw.nl/taken/cec996f4-2efa-4307-a035-32c2c9032e89"
                    }
                ],
                "status": "gereed",
                "prijs": "20.20",
                "frequentie": "eenmalig",
                "verbruiksobject": {"uren": 130},
                "dataobject": {"max_uren": 150},
            },
            response_only=True,
        ),
        OpenApiExample(
            "product request",
            value={
                "naam": "verhuurvergunning: straatweg 14",
                "start_datum": "2024-12-01",
                "eind_datum": "2026-12-01",
                "producttype_uuid": "95792000-d57f-4d3a-b14c-c4c7aa964907",
                "gepubliceerd": False,
                "eigenaren": [
                    {"bsn": "111222333"},
                ],
                "documenten": [{"uuid": "99a8bd4f-4144-4105-9850-e477628852fc"}],
                "zaken": [{"uuid": "eb188bea-51f2-44f0-8acc-eec1c710b4bf"}],
                "taken": [{"uuid": "cec996f4-2efa-4307-a035-32c2c9032e89"}],
                "status": "gereed",
                "prijs": "20.20",
                "frequentie": "eenmalig",
                "verbruiksobject": {"uren": 130},
                "dataobject": {"max_uren": 150},
            },
            request_only=True,
        ),
    ],
)
class ProductSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="product-detail", lookup_field="uuid"
    )
    producttype = NestedProductTypeSerializer(read_only=True)
    producttype_uuid = UUIDRelatedField(
        write_only=True, queryset=ProductType.objects.all(), source="producttype"
    )
    eigenaren = EigenaarSerializer(many=True)
    documenten = NestedDocumentSerializer(many=True, required=False)
    zaken = NestedZaakSerializer(many=True, required=False)
    taken = NestedTaakSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            "uuid",
            "url",
            "naam",
            "start_datum",
            "eind_datum",
            "aanmaak_datum",
            "update_datum",
            "producttype",
            "producttype_uuid",
            "gepubliceerd",
            "eigenaren",
            "documenten",
            "zaken",
            "taken",
            "status",
            "prijs",
            "frequentie",
            "verbruiksobject",
            "dataobject",
        ]
        validators = [
            DateValidator(),
            StatusValidator(),
            VerbruiksObjectValidator(),
            DataObjectValidator(),
            NestedObjectsValidator("eigenaren", Eigenaar),
        ]

    def validate_eigenaren(self, eigenaren: list[Eigenaar]) -> list[Eigenaar]:
        if len(eigenaren) == 0:
            raise serializers.ValidationError(_("Er is minimaal één eigenaar vereist."))
        return eigenaren

    def validate_documenten(self, documenten: list[dict]):
        check_externe_verwijzing_config_url("documenten_url")

        return validate_key_value_model_keys(
            documenten,
            "uuid",
            _("Er bestaat al een document met de uuid {} voor dit Product."),
        )

    def validate_zaken(self, zaken: list[dict]):
        check_externe_verwijzing_config_url("zaken_url")

        return validate_key_value_model_keys(
            zaken,
            "uuid",
            _("Er bestaat al een zaak met de uuid {} voor dit Product."),
        )

    def validate_taken(self, taken: list[dict]):
        check_externe_verwijzing_config_url("taken_url")

        return validate_key_value_model_keys(
            taken,
            "uuid",
            _("Er bestaat al een taak met de uuid {} voor dit Product."),
        )

    @transaction.atomic()
    def create(self, validated_data):
        eigenaren = validated_data.pop("eigenaren", [])
        documenten = validated_data.pop("documenten", [])
        zaken = validated_data.pop("zaken", [])
        taken = validated_data.pop("taken", [])

        product = super().create(validated_data)

        for eigenaar in eigenaren:
            eigenaar.pop("uuid", None)
            EigenaarSerializer().create(eigenaar | {"product": product})

        set_nested_serializer(
            [document | {"product": product.pk} for document in documenten],
            DocumentSerializer,
        )

        set_nested_serializer(
            [zaak | {"product": product.pk} for zaak in zaken],
            ZaakSerializer,
        )

        set_nested_serializer(
            [taak | {"product": product.pk} for taak in taken],
            TaakSerializer,
        )

        return product

    @transaction.atomic()
    def update(self, instance, validated_data):
        eigenaren = validated_data.pop("eigenaren", None)
        documenten = validated_data.pop("documenten", None)
        zaken = validated_data.pop("zaken", None)
        taken = validated_data.pop("taken", None)

        product = super().update(instance, validated_data)

        if eigenaren is not None:
            current_eigenaren_uuids = set(
                product.eigenaren.values_list("uuid", flat=True)
            )
            seen_eigenaren_uuids = set()

            for eigenaar in eigenaren:
                eigenaar_uuid = eigenaar.pop("uuid", None)
                if eigenaar_uuid is None:
                    EigenaarSerializer().create(eigenaar | {"product": product})

                else:
                    existing_eigenaar = Eigenaar.objects.get(uuid=eigenaar_uuid)
                    EigenaarSerializer().update(existing_eigenaar, eigenaar)
                    seen_eigenaren_uuids.add(eigenaar_uuid)

            product.eigenaren.filter(
                uuid__in=(current_eigenaren_uuids - seen_eigenaren_uuids)
            ).delete()

        if documenten is not None:
            instance.documenten.all().delete()
            set_nested_serializer(
                [document | {"product": instance.pk} for document in documenten],
                DocumentSerializer,
            )

        if zaken is not None:
            instance.zaken.all().delete()
            set_nested_serializer(
                [zaak | {"product": instance.pk} for zaak in zaken],
                ZaakSerializer,
            )

        if taken is not None:
            instance.taken.all().delete()
            set_nested_serializer(
                [taak | {"product": instance.pk} for taak in taken],
                TaakSerializer,
            )

        return product
