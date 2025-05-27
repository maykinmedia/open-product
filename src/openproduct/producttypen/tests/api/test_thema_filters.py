from uuid import uuid4

from django.urls import reverse_lazy

from freezegun import freeze_time
from rest_framework import status

from openproduct.producttypen.tests.factories import ProductTypeFactory, ThemaFactory
from openproduct.utils.tests.cases import BaseApiTestCase


class TestThemaFilters(BaseApiTestCase):
    path = reverse_lazy("thema-list")

    def test_gepubliceerd_filter(self):
        ThemaFactory.create(gepubliceerd=True)
        ThemaFactory.create(gepubliceerd=False)

        response = self.client.get(self.path, {"gepubliceerd": "true"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["gepubliceerd"], True)

    def test_naam_filter(self):
        ThemaFactory.create(naam="organisatie a")
        ThemaFactory.create(naam="organisatie b")

        response = self.client.get(self.path, {"naam": "organisatie b"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["naam"], "organisatie b")

    def test_hoofd_thema_naam_filter(self):
        hoofd_thema = ThemaFactory.create(naam="vervoer")
        ThemaFactory.create(hoofd_thema=hoofd_thema)
        ThemaFactory.create()

        response = self.client.get(self.path, {"hoofd_thema__naam": "vervoer"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(
            response.data["resultaten"][0]["hoofd_thema"], hoofd_thema.uuid
        )

    def test_hoofd_thema_uuid_filter(self):
        hoofd_thema_uuid = uuid4()
        hoofd_thema = ThemaFactory.create(uuid=hoofd_thema_uuid)
        ThemaFactory.create(hoofd_thema=hoofd_thema)
        ThemaFactory.create()

        response = self.client.get(self.path + f"?hoofd_thema__uuid={hoofd_thema_uuid}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(
            response.data["resultaten"][0]["hoofd_thema"], hoofd_thema_uuid
        )

    def test_aanmaak_datum_filter(self):
        with freeze_time("2024-06-07"):
            ThemaFactory.create()
        with freeze_time("2025-06-07"):
            ThemaFactory.create()

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
            ThemaFactory.create()
        with freeze_time("2025-06-07"):
            ThemaFactory.create()

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

    def test_producttypen_uuid_filter(self):
        producttype1 = ProductTypeFactory()
        producttype2 = ProductTypeFactory()
        producttype3 = ProductTypeFactory()

        thema1 = ThemaFactory()
        thema2 = ThemaFactory()
        thema3 = ThemaFactory()

        thema1.producttypen.set([producttype1, producttype2])
        thema2.producttypen.add(producttype2)
        thema3.producttypen.add(producttype3)

        with self.subTest("exact filter"):
            response = self.client.get(
                self.path, {"producttypen__uuid": str(producttype1.uuid)}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["aantal"], 1)
            self.assertEqual(response.data["resultaten"][0]["uuid"], str(thema1.uuid))

        with self.subTest("in filter"):
            uuids_in = f"{producttype1.uuid},{producttype2.uuid}"
            response = self.client.get(self.path, {"producttypen__uuid__in": uuids_in})

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            returned_uuids = {result["uuid"] for result in response.data["resultaten"]}

            self.assertIn(str(thema1.uuid), returned_uuids)
            self.assertIn(str(thema2.uuid), returned_uuids)
            self.assertNotIn(str(thema3.uuid), returned_uuids)

        with self.subTest("distinct"):
            uuids_in = f"{producttype1.uuid},{producttype2.uuid}"
            response = self.client.get(self.path, {"producttypen__uuid__in": uuids_in})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            result_uuids = [result["uuid"] for result in response.data["resultaten"]]
            self.assertEqual(result_uuids.count(str(thema1.uuid)), 1)
