from datetime import date
from decimal import Decimal
from uuid import uuid4

from django.urls import reverse_lazy

from rest_framework import status

from openproduct.producttypen.tests.factories import (
    PrijsFactory,
    PrijsOptieFactory,
    PrijsRegelFactory,
)
from openproduct.utils.tests.cases import BaseApiTestCase


class TestPrijsFilters(BaseApiTestCase):
    path = reverse_lazy("prijs-list")

    def test_prijs_opties_bedrag_filter(self):
        prijs1 = PrijsFactory.create()
        PrijsOptieFactory.create(prijs=prijs1, bedrag=Decimal(10))
        PrijsOptieFactory.create(prijs=prijs1, bedrag=Decimal(30))
        prijs2 = PrijsFactory.create()
        PrijsOptieFactory.create(prijs=prijs2, bedrag=Decimal(50))

        with self.subTest("exact"):
            response = self.client.get(self.path, {"prijsopties__bedrag": "50"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(response.data["resultaten"][0]["uuid"], str(prijs2.uuid))

        with self.subTest("lte"):
            response = self.client.get(self.path, {"prijsopties__bedrag__lte": "40"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(response.data["resultaten"][0]["uuid"], str(prijs1.uuid))

        with self.subTest("gte"):
            response = self.client.get(self.path, {"prijsopties__bedrag__gte": "40"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(response.data["resultaten"][0]["uuid"], str(prijs2.uuid))

    def test_prijs_opties_beschrijving_filter(self):
        prijs = PrijsFactory.create()
        PrijsFactory.create()

        PrijsOptieFactory.create(prijs=prijs, beschrijving="spoed")

        response = self.client.get(self.path, {"prijsopties__beschrijving": "spoed"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["uuid"], str(prijs.uuid))

    def test_prijs_regels_dmn_tabel_id_filter(self):
        prijs = PrijsFactory.create()
        PrijsFactory.create()

        PrijsRegelFactory.create(
            prijs=prijs, dmn_tabel_id="a4dcf122-e224-48f9-8c09-79e5bbb10154"
        )

        response = self.client.get(
            self.path,
            {"prijsregels__dmn_tabel_id": "a4dcf122-e224-48f9-8c09-79e5bbb10154"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["uuid"], str(prijs.uuid))

    def test_prijs_regels_beschrijving_filter(self):
        prijs = PrijsFactory.create()
        PrijsFactory.create()

        PrijsRegelFactory.create(prijs=prijs, beschrijving="base")

        response = self.client.get(self.path, {"prijsregels__beschrijving": "base"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["uuid"], str(prijs.uuid))

    def test_actief_vanaf_filter(self):
        PrijsFactory.create(actief_vanaf=date(2024, 6, 7))
        PrijsFactory.create(actief_vanaf=date(2025, 6, 7))

        with self.subTest("exact"):
            response = self.client.get(self.path, {"actief_vanaf": "2024-06-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["actief_vanaf"], "2024-06-07"
            )

        with self.subTest("lte"):
            response = self.client.get(self.path, {"actief_vanaf__lte": "2024-07-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["actief_vanaf"], "2024-06-07"
            )

        with self.subTest("gte"):
            response = self.client.get(self.path, {"actief_vanaf__gte": "2025-04-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(
                response.data["resultaten"][0]["actief_vanaf"], "2025-06-07"
            )

    def test_producttype_code_filter(self):
        producttype_uuid = uuid4()
        PrijsFactory.create(producttype__code="123")
        PrijsFactory.create(
            producttype__code="8234098q2730492873", producttype__uuid=producttype_uuid
        )

        response = self.client.get(
            self.path, {"producttype__code": "8234098q2730492873"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(
            response.data["resultaten"][0]["producttype_uuid"], producttype_uuid
        )

    def test_producttype_uuid_filter(self):
        producttype_uuid = uuid4()
        PrijsFactory.create(producttype__uuid=producttype_uuid)
        PrijsFactory.create(producttype__uuid=uuid4())

        response = self.client.get(self.path + f"?producttype__uuid={producttype_uuid}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(
            response.data["resultaten"][0]["producttype_uuid"], producttype_uuid
        )

    def test_producttype_upn_filter(self):
        producttype_uuid = uuid4()
        PrijsFactory.create(
            producttype__uniforme_product_naam__naam="parkeervergunning",
            producttype__uuid=producttype_uuid,
        )
        PrijsFactory.create(producttype__uniforme_product_naam__naam="aanbouw")

        response = self.client.get(
            self.path, {"uniforme_product_naam": "parkeervergunning"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(
            response.data["resultaten"][0]["producttype_uuid"], producttype_uuid
        )

    def test_producttype_naam_filter(self):
        producttype_uuid = uuid4()
        PrijsFactory.create(
            producttype__naam="parkeervergunning", producttype__uuid=producttype_uuid
        )
        PrijsFactory.create(producttype__naam="aanbouw")

        response = self.client.get(
            self.path, {"producttype__naam": "parkeervergunning"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(
            response.data["resultaten"][0]["producttype_uuid"], producttype_uuid
        )
