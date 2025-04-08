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

    def test_producttype_code_filter(self):
        producttype_uuid = uuid4()
        BestandFactory.create(producttype__code="123")
        BestandFactory.create(
            producttype__code="8234098q2730492873",
            producttype__uuid=producttype_uuid,
        )

        response = self.client.get(
            self.path, {"producttype__code": "8234098q2730492873"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["producttype_uuid"], producttype_uuid
        )

    def test_producttype_uuid_filter(self):
        producttype_uuid = uuid4()
        BestandFactory.create(producttype__uuid=producttype_uuid)
        BestandFactory.create(producttype__uuid=uuid4())

        response = self.client.get(self.path + f"?producttype__uuid={producttype_uuid}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["producttype_uuid"], producttype_uuid
        )

    def test_producttype_upn_filter(self):
        producttype_uuid = uuid4()
        BestandFactory.create(
            producttype__uniforme_product_naam__naam="parkeervergunning",
            producttype__uuid=producttype_uuid,
        )
        BestandFactory.create(producttype__uniforme_product_naam__naam="aanbouw")

        response = self.client.get(
            self.path, {"uniforme_product_naam": "parkeervergunning"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["producttype_uuid"], producttype_uuid
        )

    def test_producttype_naam_filter(self):
        producttype_uuid = uuid4()
        BestandFactory.create(
            producttype__naam="parkeervergunning", producttype__uuid=producttype_uuid
        )
        BestandFactory.create(producttype__naam="aanbouw")

        response = self.client.get(
            self.path, {"producttype__naam": "parkeervergunning"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["producttype_uuid"], producttype_uuid
        )
