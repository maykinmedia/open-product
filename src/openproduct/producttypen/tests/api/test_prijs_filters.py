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
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["id"], str(prijs2.id))

        with self.subTest("lte"):
            response = self.client.get(self.path, {"prijsopties__bedrag__lte": "40"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["id"], str(prijs1.id))

        with self.subTest("gte"):
            response = self.client.get(self.path, {"prijsopties__bedrag__gte": "40"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["id"], str(prijs2.id))

    def test_prijs_opties_beschrijving_filter(self):
        prijs = PrijsFactory.create()
        PrijsFactory.create()

        PrijsOptieFactory.create(prijs=prijs, beschrijving="spoed")

        response = self.client.get(self.path, {"prijsopties__beschrijving": "spoed"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], str(prijs.id))

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
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], str(prijs.id))

    def test_prijs_regels_beschrijving_filter(self):
        prijs = PrijsFactory.create()
        PrijsFactory.create()

        PrijsRegelFactory.create(prijs=prijs, beschrijving="base")

        response = self.client.get(self.path, {"prijsregels__beschrijving": "base"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], str(prijs.id))

    def test_actief_vanaf_filter(self):
        PrijsFactory.create(actief_vanaf=date(2024, 6, 7))
        PrijsFactory.create(actief_vanaf=date(2025, 6, 7))

        with self.subTest("exact"):
            response = self.client.get(self.path, {"actief_vanaf": "2024-06-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["actief_vanaf"], "2024-06-07")

        with self.subTest("lte"):
            response = self.client.get(self.path, {"actief_vanaf__lte": "2024-07-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["actief_vanaf"], "2024-06-07")

        with self.subTest("gte"):
            response = self.client.get(self.path, {"actief_vanaf__gte": "2025-04-07"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["actief_vanaf"], "2025-06-07")

    def test_producttype_code_filter(self):
        producttype_id = uuid4()
        PrijsFactory.create(producttype__code="123")
        PrijsFactory.create(
            producttype__code="8234098q2730492873", producttype__id=producttype_id
        )

        response = self.client.get(
            self.path, {"producttype__code": "8234098q2730492873"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["producttype_id"], producttype_id)

    def test_producttype_id_filter(self):
        producttype_id = uuid4()
        PrijsFactory.create(producttype__id=producttype_id)
        PrijsFactory.create(producttype__id=uuid4())

        response = self.client.get(self.path + f"?producttype__id={producttype_id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["producttype_id"], producttype_id)

    def test_producttype_upn_filter(self):
        producttype_id = uuid4()
        PrijsFactory.create(
            producttype__uniforme_product_naam__naam="parkeervergunning",
            producttype__id=producttype_id,
        )
        PrijsFactory.create(producttype__uniforme_product_naam__naam="aanbouw")

        response = self.client.get(
            self.path, {"uniforme_product_naam": "parkeervergunning"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["producttype_id"], producttype_id)

    def test_producttype_naam_filter(self):
        producttype_id = uuid4()
        PrijsFactory.create(
            producttype__naam="parkeervergunning", producttype__id=producttype_id
        )
        PrijsFactory.create(producttype__naam="aanbouw")

        response = self.client.get(
            self.path, {"producttype__naam": "parkeervergunning"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["producttype_id"], producttype_id)
