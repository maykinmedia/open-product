from datetime import date
from decimal import Decimal
from uuid import uuid4

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from freezegun import freeze_time
from rest_framework import status
from rest_framework.exceptions import ErrorDetail

from openproduct.producten.models.product import PrijsFrequentieChoices
from openproduct.producten.tests.factories import (
    DocumentFactory,
    EigenaarFactory,
    ProductFactory,
    TaakFactory,
    ZaakFactory,
)
from openproduct.producttypen.models.producttype import ProductStateChoices
from openproduct.producttypen.tests.factories import (
    JsonSchemaFactory,
    ProductTypeFactory,
)
from openproduct.utils.tests.cases import BaseApiTestCase


class TestProductFilters(BaseApiTestCase):
    path = reverse_lazy("product-list")

    def test_gepubliceerd_filter(self):
        ProductFactory.create(gepubliceerd=True)
        ProductFactory.create(gepubliceerd=False)

        response = self.client.get(self.path, {"gepubliceerd": "true"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["gepubliceerd"], True)

    def test_status_filter(self):
        ProductFactory.create(status=ProductStateChoices.INITIEEL)
        ProductFactory.create(status=ProductStateChoices.GEREED)

        response = self.client.get(self.path, {"status": "initieel"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["status"], "initieel")

    def test_frequentie_filter(self):
        ProductFactory.create(frequentie=PrijsFrequentieChoices.EENMALIG)
        ProductFactory.create(frequentie=PrijsFrequentieChoices.MAANDELIJKS)

        response = self.client.get(self.path, {"frequentie": "eenmalig"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["frequentie"], "eenmalig")

    def test_prijs_filter(self):
        ProductFactory.create(prijs=Decimal("10"))
        ProductFactory.create(prijs=Decimal("20.99"))

        with self.subTest("exact"):
            response = self.client.get(self.path, {"prijs": "20.99"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(response.data["resultaten"][0]["prijs"], "20.99")

        with self.subTest("lte"):
            response = self.client.get(self.path, {"prijs__lte": "20"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(response.data["resultaten"][0]["prijs"], "10.00")

        with self.subTest("gte"):
            response = self.client.get(self.path, {"prijs__gte": "20"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(response.data["resultaten"][0]["prijs"], "20.99")

    def test_producttype_code_filter(self):
        ProductFactory.create(producttype__code="123")
        ProductFactory.create(producttype__code="8234098q2730492873")

        with self.subTest("exact"):
            response = self.client.get(
                self.path, {"producttype__code": "8234098q2730492873"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["producttype"]["code"],
                "8234098q2730492873",
            )

        with self.subTest("in"):
            response = self.client.get(
                self.path,
                {"producttype__code__in": "8234098q2730492873,123"},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 2)

    def test_producttype_upn_filter(self):
        ProductFactory.create(
            producttype__uniforme_product_naam__naam="parkeervergunning"
        )
        ProductFactory.create(producttype__uniforme_product_naam__naam="aanbouw")

        response = self.client.get(
            self.path, {"uniforme_product_naam": "parkeervergunning"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(
            response.data["resultaten"][0]["producttype"]["uniforme_product_naam"],
            "parkeervergunning",
        )

    def test_producttype_uuid_filter(self):
        producttype_uuid = uuid4()
        producttype_uuid_2 = uuid4()
        ProductFactory.create(producttype__uuid=producttype_uuid)
        ProductFactory.create(producttype__uuid=producttype_uuid_2)

        with self.subTest("exact"):
            response = self.client.get(
                self.path, {"producttype__uuid": str(producttype_uuid)}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["producttype"]["uuid"],
                str(producttype_uuid),
            )

        with self.subTest("in"):
            response = self.client.get(
                self.path,
                {"producttype__uuid__in": f"{producttype_uuid},{producttype_uuid_2}"},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 2)

    def test_producttype_naam_filter(self):
        producttype_uuid = uuid4()
        ProductFactory.create(
            producttype__naam="parkeervergunning", producttype__uuid=producttype_uuid
        )
        ProductFactory.create(producttype__naam="aanbouw")

        with self.subTest("exact"):
            response = self.client.get(
                self.path, {"producttype__naam": "parkeervergunning"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["producttype"]["uuid"],
                str(producttype_uuid),
            )

        with self.subTest("in"):
            response = self.client.get(
                self.path, {"producttype__naam__in": "parkeervergunning,aanbouw"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 2)

    def test_start_datum_filter(self):
        ProductFactory.create(start_datum=date(2024, 6, 7))
        ProductFactory.create(start_datum=date(2025, 6, 7))

        with self.subTest("exact"):
            response = self.client.get(self.path, {"start_datum": "2024-06-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["start_datum"], "2024-06-07"
            )

        with self.subTest("lte"):
            response = self.client.get(self.path, {"start_datum__lte": "2024-07-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["start_datum"], "2024-06-07"
            )

        with self.subTest("gte"):
            response = self.client.get(self.path, {"start_datum__gte": "2025-04-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["start_datum"], "2025-06-07"
            )

    def test_eind_datum_filter(self):
        ProductFactory.create(eind_datum=date(2024, 6, 7))
        ProductFactory.create(eind_datum=date(2025, 6, 7))

        with self.subTest("exact"):
            response = self.client.get(self.path, {"eind_datum": "2024-06-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(response.data["resultaten"][0]["eind_datum"], "2024-06-07")

        with self.subTest("lte"):
            response = self.client.get(self.path, {"eind_datum__lte": "2024-07-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(response.data["resultaten"][0]["eind_datum"], "2024-06-07")

        with self.subTest("gte"):
            response = self.client.get(self.path, {"eind_datum__gte": "2025-04-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(response.data["resultaten"][0]["eind_datum"], "2025-06-07")

    def test_aanmaak_datum_filter(self):
        with freeze_time("2024-06-07"):
            ProductFactory.create()
        with freeze_time("2025-06-07"):
            ProductFactory.create()

        with self.subTest("exact"):
            response = self.client.get(
                self.path, {"aanmaak_datum": "2024-06-07T00:00:00+00:00"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["aanmaak_datum"],
                "2024-06-07T02:00:00+02:00",
            )

        with self.subTest("lte"):
            response = self.client.get(self.path, {"aanmaak_datum__lte": "2024-07-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["aanmaak_datum"],
                "2024-06-07T02:00:00+02:00",
            )

        with self.subTest("gte"):
            response = self.client.get(self.path, {"aanmaak_datum__gte": "2025-04-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["aanmaak_datum"],
                "2025-06-07T02:00:00+02:00",
            )

    def test_update_datum_filter(self):
        with freeze_time("2024-06-07"):
            ProductFactory.create()
        with freeze_time("2025-06-07"):
            ProductFactory.create()

        with self.subTest("exact"):
            response = self.client.get(
                self.path, {"update_datum": "2024-06-07T00:00:00+00:00"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["update_datum"],
                "2024-06-07T02:00:00+02:00",
            )

        with self.subTest("lte"):
            response = self.client.get(self.path, {"update_datum__lte": "2024-07-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["update_datum"],
                "2024-06-07T02:00:00+02:00",
            )

        with self.subTest("gte"):
            response = self.client.get(self.path, {"update_datum__gte": "2025-04-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["update_datum"],
                "2025-06-07T02:00:00+02:00",
            )

    def test_dataobject_attr_string_filters(self):
        schema = {
            "type": "object",
            "properties": {"naam": {"type": "string"}},
            "required": ["naam"],
        }

        ProductFactory(
            producttype=ProductTypeFactory.create(
                dataobject_schema=JsonSchemaFactory(schema=schema)
            ),
            dataobject={"naam": "test"},
        )

        ProductFactory(
            producttype=ProductTypeFactory.create(
                dataobject_schema=JsonSchemaFactory(schema=schema)
            ),
            dataobject={"naam": "abc"},
        )

        with self.subTest("exact"):
            response = self.client.get(
                self.path, {"dataobject_attr": "naam__exact__test"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["dataobject"]["naam"], "test"
            )

        with self.subTest("icontains"):
            response = self.client.get(
                self.path, {"dataobject_attr": "naam__icontains__st"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["dataobject"]["naam"], "test"
            )

        with self.subTest("in"):
            response = self.client.get(
                self.path, {"dataobject_attr": "naam__in__test|abc"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 2)

        for op in ["gt", "gte", "lt", "lte"]:
            with self.subTest(op):
                response = self.client.get(
                    self.path, {"dataobject_attr": f"naam__{op}__abc"}
                )

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verbruiksobject_attr_string_filters(self):
        schema = {
            "type": "object",
            "properties": {"naam": {"type": "string"}},
            "required": ["naam"],
        }

        ProductFactory(
            producttype=ProductTypeFactory.create(
                verbruiksobject_schema=JsonSchemaFactory(schema=schema)
            ),
            verbruiksobject={"naam": "test"},
        )

        ProductFactory(
            producttype=ProductTypeFactory.create(
                verbruiksobject_schema=JsonSchemaFactory(schema=schema)
            ),
            verbruiksobject={"naam": "abc"},
        )

        with self.subTest("exact"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "naam__exact__test"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["verbruiksobject"]["naam"], "test"
            )

        with self.subTest("icontains"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "naam__icontains__st"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["verbruiksobject"]["naam"], "test"
            )

        with self.subTest("in"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "naam__in__test|abc"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 2)

        for op in ["gt", "gte", "lt", "lte"]:
            with self.subTest(op):
                response = self.client.get(
                    self.path, {"verbruiksobject_attr": f"naam__{op}__abc"}
                )

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verbruiksobject_attr_numeric_filters(self):
        schema = {
            "type": "object",
            "properties": {"leeftijd": {"type": "number"}},
            "required": ["leeftijd"],
        }

        ProductFactory(
            producttype=ProductTypeFactory.create(
                verbruiksobject_schema=JsonSchemaFactory(schema=schema)
            ),
            verbruiksobject={"leeftijd": 30},
        )

        ProductFactory(
            producttype=ProductTypeFactory.create(
                verbruiksobject_schema=JsonSchemaFactory(schema=schema)
            ),
            verbruiksobject={"leeftijd": 50},
        )

        with self.subTest("exact"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "leeftijd__exact__30"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["verbruiksobject"]["leeftijd"], 30.0
            )

        with self.subTest("icontains"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "leeftijd__icontains__30"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["verbruiksobject"]["leeftijd"], 30
            )

        with self.subTest("in"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "leeftijd__in__30|50"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 2)

        with self.subTest("gt"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "leeftijd__gt__40"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["verbruiksobject"]["leeftijd"], 50
            )

        with self.subTest("gte"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "leeftijd__gte__50"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["verbruiksobject"]["leeftijd"], 50
            )

        with self.subTest("lt"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "leeftijd__lt__40"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["verbruiksobject"]["leeftijd"], 30
            )

        with self.subTest("lte"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "leeftijd__lte__30"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["verbruiksobject"]["leeftijd"], 30
            )

    def test_verbruiksobject_attr_date_filters(self):
        schema = {
            "type": "object",
            "properties": {"datum": {"type": "date"}},
            "required": ["datum"],
        }

        ProductFactory(
            producttype=ProductTypeFactory.create(
                verbruiksobject_schema=JsonSchemaFactory(schema=schema)
            ),
            verbruiksobject={"datum": "2024-10-10"},
        )

        ProductFactory(
            producttype=ProductTypeFactory.create(
                verbruiksobject_schema=JsonSchemaFactory(schema=schema)
            ),
            verbruiksobject={"datum": "2025-10-10"},
        )

        with self.subTest("none"):
            response = self.client.get(self.path)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("exact"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "datum__exact__2024-10-10"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["verbruiksobject"]["datum"],
                "2024-10-10",
            )

        with self.subTest("icontains"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "datum__icontains__2024"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["verbruiksobject"]["datum"],
                "2024-10-10",
            )

        with self.subTest("in"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "datum__in__2024-10-10|2025-10-10"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 2)

        with self.subTest("gt"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "datum__gt__2024-12-10"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["verbruiksobject"]["datum"],
                "2025-10-10",
            )

        with self.subTest("gte"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "datum__gte__2025-10-10"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["verbruiksobject"]["datum"],
                "2025-10-10",
            )

        with self.subTest("lt"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "datum__lt__2024-12-10"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["verbruiksobject"]["datum"],
                "2024-10-10",
            )

        with self.subTest("lte"):
            response = self.client.get(
                self.path, {"verbruiksobject_attr": "datum__lte__2024-10-10"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["verbruiksobject"]["datum"],
                "2024-10-10",
            )

    def test_verbruiksobject_attr_filter_with_comma(self):
        filter = "naam__icontains__test,naam__icontains__abc"

        response = self.client.get(
            self.path,
            {"verbruiksobject_attr": filter},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            [
                ErrorDetail(
                    string=_(
                        "Filter '{}' moet de format 'key__operator__value' hebben, "
                        "komma's kunnen alleen in de `waarde` worden toegevoegd"
                    ).format(filter),
                    code="invalid-data-attr-query",
                )
            ],
        )

    def test_verbruiksobject_attr_filter_with_wrong_shape(self):
        filter = "naam__icontains"

        response = self.client.get(
            self.path,
            {"verbruiksobject_attr": filter},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            [
                ErrorDetail(
                    string=_(
                        "Filter '{}' heeft niet de format 'key__operator__waarde'"
                    ).format(filter),
                    code="invalid-data-attr-query",
                )
            ],
        )

    def test_verbruiksobject_attr_filter_with_unknown_operator(self):
        response = self.client.get(
            self.path,
            {"verbruiksobject_attr": "naam__contains__test"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            [
                ErrorDetail(
                    string=_("operator `{}` is niet bekend/ondersteund").format(
                        "contains"
                    ),
                    code="invalid-data-attr-query",
                )
            ],
        )

    def test_verbruiksobject_attr_multiple_filters(self):
        schema = {
            "type": "object",
            "properties": {"naam": {"type": "string"}, "type": "string"},
            "required": ["naam"],
        }

        ProductFactory(
            producttype=ProductTypeFactory.create(
                verbruiksobject_schema=JsonSchemaFactory(schema=schema)
            ),
            verbruiksobject={"naam": "test", "type": "test"},
        )

        ProductFactory(
            producttype=ProductTypeFactory.create(
                verbruiksobject_schema=JsonSchemaFactory(schema=schema)
            ),
            verbruiksobject={"naam": "abc", "type": "abc"},
        )

        response = self.client.get(
            self.path,
            {"verbruiksobject_attr": ("naam__exact__test", "type__exact__test")},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(
            response.data["resultaten"][0]["verbruiksobject"]["naam"], "test"
        )

    def test_document_uuid_filter(self):
        uuid = uuid4()

        DocumentFactory.create(uuid=uuid)
        DocumentFactory.create()

        response = self.client.get(self.path, {"documenten__uuid": uuid})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertIn(str(uuid), response.data["resultaten"][0]["documenten"][0]["url"])

    def test_zaak_uuid_filter(self):
        uuid = uuid4()

        ZaakFactory.create(uuid=uuid)
        ZaakFactory.create()

        response = self.client.get(self.path, {"zaken__uuid": uuid})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertIn(str(uuid), response.data["resultaten"][0]["zaken"][0]["url"])

    def test_taak_uuid_filter(self):
        uuid = uuid4()

        TaakFactory.create(uuid=uuid)
        TaakFactory.create()

        response = self.client.get(self.path, {"taken__uuid": uuid})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertIn(str(uuid), response.data["resultaten"][0]["taken"][0]["url"])

    def test_eigenaar_uuid_filter(self):
        uuid = uuid4()

        product = ProductFactory.create()
        product.eigenaren.add(EigenaarFactory(uuid=uuid))
        product.save()

        product_2 = ProductFactory.create()
        product_2.eigenaren.add(EigenaarFactory(uuid=uuid4()))
        product_2.save()

        response = self.client.get(self.path, {"eigenaren__uuid": str(uuid)})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(
            response.data["resultaten"][0]["eigenaren"][0]["uuid"], str(uuid)
        )

    def test_eigenaar_bsn_filter(self):
        product = ProductFactory.create()
        product.eigenaren.add(EigenaarFactory(bsn="111222333"))
        product.save()

        product_2 = ProductFactory.create()
        product_2.eigenaren.add(EigenaarFactory(bsn="999998328"))
        product_2.save()

        with self.subTest("exact"):
            response = self.client.get(self.path, {"eigenaren__bsn": "111222333"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["eigenaren"][0]["bsn"], "111222333"
            )

        with self.subTest("distinct"):
            product.eigenaren.add(EigenaarFactory(bsn="111222333"))
            product.save()

            response = self.client.get(self.path, {"eigenaren__bsn": "111222333"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["eigenaren"][0]["bsn"], "111222333"
            )

    def test_eigenaar_kvk_nummer_filter(self):
        product = ProductFactory.create()
        product.eigenaren.add(EigenaarFactory(kvk_nummer="12345678"))
        product.save()

        product_2 = ProductFactory.create()
        product_2.eigenaren.add(EigenaarFactory(kvk_nummer="87654321"))
        product_2.save()

        with self.subTest("exact"):
            response = self.client.get(self.path, {"eigenaren__kvk_nummer": "12345678"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["eigenaren"][0]["kvk_nummer"],
                "12345678",
            )

        with self.subTest("distinct"):
            product.eigenaren.add(EigenaarFactory(kvk_nummer="12345678"))
            product.save()

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["eigenaren"][0]["kvk_nummer"],
                "12345678",
            )

    def test_eigenaar_klantnummer_filter(self):
        product = ProductFactory.create()
        product.eigenaren.add(EigenaarFactory(klantnummer="12345678"))
        product.save()

        product_2 = ProductFactory.create()
        product_2.eigenaren.add(EigenaarFactory(klantnummer="87654321"))
        product_2.save()

        with self.subTest("exact"):
            response = self.client.get(
                self.path, {"eigenaren__klantnummer": "12345678"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["eigenaren"][0]["klantnummer"],
                "12345678",
            )

        with self.subTest("distinct"):
            product.eigenaren.add(EigenaarFactory(klantnummer="12345678"))
            product.save()

            response = self.client.get(
                self.path, {"eigenaren__klantnummer": "12345678"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["eigenaren"][0]["klantnummer"],
                "12345678",
            )

    def test_eigenaar_vestigingsnummer_filter(self):
        product = ProductFactory.create()
        product.eigenaren.add(EigenaarFactory(vestigingsnummer="12345678"))
        product.save()

        product_2 = ProductFactory.create()
        product_2.eigenaren.add(EigenaarFactory(vestigingsnummer="87654321"))
        product_2.save()

        with self.subTest("exact"):
            response = self.client.get(
                self.path, {"eigenaren__vestigingsnummer": "12345678"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["eigenaren"][0]["vestigingsnummer"],
                "12345678",
            )

        with self.subTest("distinct"):
            response = self.client.get(
                self.path, {"eigenaren__vestigingsnummer": "12345678"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["eigenaren"][0]["vestigingsnummer"],
                "12345678",
            )

    def test_naam_filter(self):
        product_1 = ProductFactory.create(naam="Verhuurvergunning Mijnstraat 42")
        ProductFactory.create(naam="Verhuurvergunning Laan 15")
        with self.subTest("exact"):
            response = self.client.get(
                self.path, {"naam": "Verhuurvergunning Mijnstraat 42"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["uuid"], str(product_1.uuid)
            )
            self.assertEqual(
                response.data["resultaten"][0]["naam"],
                "Verhuurvergunning Mijnstraat 42",
            )
