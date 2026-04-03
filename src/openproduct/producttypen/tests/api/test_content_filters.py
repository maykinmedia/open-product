from uuid import uuid4

from django.urls import reverse_lazy

from rest_framework import status

from openproduct.producttypen.tests.factories import (
    ContentElementFactory,
    ProductTypeFactory,
    ThemaFactory,
    ZaakTypeFactory,
)
from openproduct.utils.tests.cases import BaseApiTestCase


class TestContentFilters(BaseApiTestCase):
    is_superuser = True
    path = reverse_lazy("content-list")

    def test_content_contains(self):
        ContentElementFactory.create(content="abc")
        ContentElementFactory.create(content="test")

        response = self.client.get(self.path, {"content__contains": "a"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["content"], "abc")

    def test_producttype_code_filter(self):
        producttype_uuid = uuid4()
        ContentElementFactory.create(producttype__code="123")
        ContentElementFactory.create(
            producttype__code="8234098q2730492873", producttype__uuid=producttype_uuid
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
        ContentElementFactory.create(producttype__uuid=producttype_uuid)
        ContentElementFactory.create(producttype__uuid=uuid4())

        response = self.client.get(self.path + f"?producttype__uuid={producttype_uuid}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["producttype_uuid"], producttype_uuid
        )

    def test_producttype_naam_filter(self):
        producttype_uuid = uuid4()
        ContentElementFactory.create(
            producttype__naam="parkeervergunning", producttype__uuid=producttype_uuid
        )
        ContentElementFactory.create(producttype__naam="aanbouw")

        response = self.client.get(
            self.path, {"producttype__naam": "parkeervergunning"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["producttype_uuid"], producttype_uuid
        )

    def test_producttype_thema_uuid_filter(self):
        uuid = uuid4()

        producttype = ProductTypeFactory.create()
        producttype.themas.add(ThemaFactory.create(uuid=uuid))
        producttype.save()

        producttype_2 = ProductTypeFactory.create()
        producttype_2.themas.add(ThemaFactory.create())
        producttype_2.save()

        ContentElementFactory.create(producttype=producttype)
        ContentElementFactory.create(producttype=producttype_2)

        response = self.client.get(self.path, {"producttype__themas__uuid": uuid})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["producttype_uuid"], producttype.uuid
        )

    def test_producttype_thema_naam_filter(self):
        producttype = ProductTypeFactory.create()
        producttype.themas.add(ThemaFactory.create(naam="thema"))
        producttype.save()

        producttype_2 = ProductTypeFactory.create()
        producttype_2.themas.add(ThemaFactory.create(naam="test"))
        producttype_2.save()

        ContentElementFactory.create(producttype=producttype)
        ContentElementFactory.create(producttype=producttype_2)

        response = self.client.get(self.path, {"producttype__themas__naam": "thema"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["producttype_uuid"], producttype.uuid
        )

    def test__thema_uuid_filter(self):
        uuid = uuid4()

        contentelement = ContentElementFactory.create(
            thema=ThemaFactory.create(uuid=uuid)
        )
        ContentElementFactory.create(thema=ThemaFactory.create())

        response = self.client.get(self.path, {"thema__uuid": uuid})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(contentelement.uuid))

    def test_thema_naam_filter(self):
        contentelement = ContentElementFactory.create(
            thema=ThemaFactory.create(naam="thema")
        )

        ContentElementFactory.create(thema=ThemaFactory.create(naam="test"))

        response = self.client.get(self.path, {"thema__naam": "thema"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(contentelement.uuid))

    def test_producttype_zaaktypen_filter(self):
        uuid = uuid4()

        producttype = ProductTypeFactory.create()
        producttype.zaaktypen.add(
            ZaakTypeFactory.create(
                urn=f"maykin:abc:ztc:zaaktype:{uuid}",
                url=f"https://maykin.ztc.com/zaaktypen/{uuid}",
            )
        )
        producttype.save()

        producttype_2 = ProductTypeFactory.create()
        producttype_2.zaaktypen.add(
            ZaakTypeFactory.create(
                urn=f"maykin:def:ztc:zaaktype:{uuid4()}",
                url=f"https://maykin.ztc.nl/zaaktypen/{uuid4()}",
            )
        )
        producttype_2.save()

        ContentElementFactory.create(producttype=producttype)
        ContentElementFactory.create(producttype=producttype_2)

        with self.subTest("urn exact"):
            response = self.client.get(
                self.path,
                {"producttype__zaaktypen__urn": f"maykin:abc:ztc:zaaktype:{uuid}"},
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["producttype_uuid"], producttype.uuid
            )

        with self.subTest("url exact"):
            response = self.client.get(
                self.path,
                {
                    "producttype__zaaktypen__url": f"https://maykin.ztc.com/zaaktypen/{uuid}"
                },
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(
                response.data["results"][0]["producttype_uuid"], producttype.uuid
            )
