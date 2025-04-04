from uuid import uuid4

from django.core.files.base import ContentFile
from django.urls import reverse_lazy

from rest_framework import status

from openproduct.producttypen.tests.factories import BestandFactory
from openproduct.utils.tests.cases import BaseApiTestCase


class TestBestandFilters(BaseApiTestCase):

    path = reverse_lazy("bestand-list")

    def test_naam_filter(self):
        bestand = BestandFactory.create(bestand=ContentFile(b"abc", "abc.txt"))
        BestandFactory.create()

        response = self.client.get(self.path, {"naam__contains": "abc"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["bestand"],
            "http://testserver" + bestand.bestand.url,
        )

    def test_product_type_code_filter(self):
        product_type_id = uuid4()
        BestandFactory.create(product_type__code="123")
        BestandFactory.create(
            product_type__code="8234098q2730492873", product_type__id=product_type_id
        )

        response = self.client.get(
            self.path, {"product_type__code": "8234098q2730492873"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["product_type_id"], product_type_id
        )

    def test_product_type_id_filter(self):
        product_type_id = uuid4()
        BestandFactory.create(product_type__id=product_type_id)
        BestandFactory.create(product_type__id=uuid4())

        response = self.client.get(self.path + f"?product_type__id={product_type_id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["product_type_id"], product_type_id
        )

    def test_product_type_upn_filter(self):
        product_type_id = uuid4()
        BestandFactory.create(
            product_type__uniforme_product_naam__naam="parkeervergunning",
            product_type__id=product_type_id,
        )
        BestandFactory.create(product_type__uniforme_product_naam__naam="aanbouw")

        response = self.client.get(
            self.path, {"uniforme_product_naam": "parkeervergunning"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["product_type_id"], product_type_id
        )

    def test_product_type_naam_filter(self):
        product_type_id = uuid4()
        BestandFactory.create(
            product_type__naam="parkeervergunning", product_type__id=product_type_id
        )
        BestandFactory.create(product_type__naam="aanbouw")

        response = self.client.get(
            self.path, {"product_type__naam": "parkeervergunning"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["product_type_id"], product_type_id
        )
