from uuid import uuid4

from django.urls import reverse_lazy

from rest_framework import status

from openproduct.producttypen.tests.factories import ActieFactory, DmnConfigFactory
from openproduct.utils.tests.cases import BaseApiTestCase


class TestActieFilters(BaseApiTestCase):
    path = reverse_lazy("actie-list")

    def test_naam_filter(self):
        ActieFactory.create(naam="verlegging")
        ActieFactory.create(naam="opzegging")

        response = self.client.get(self.path, {"naam": "verlegging"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["naam"], "verlegging")

    def test_naam_contains_filter(self):
        ActieFactory.create(naam="verlegging")
        ActieFactory.create(naam="opzegging")

        response = self.client.get(self.path, {"naam__contains": "opzeg"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["naam"], "opzegging")

    def test_dmn_tabel_id_filter(self):
        dmn_config = DmnConfigFactory(
            tabel_endpoint="https://gemeente-a-flowable/dmn-repository/decision-tables"
        )
        ActieFactory.create(
            dmn_tabel_id="46aa6b3a-c0a1-11e6-bc93-6ab56fad108a", dmn_config=dmn_config
        )
        ActieFactory.create(
            dmn_tabel_id="a4dcf122-e224-48f9-8c09-79e5bbb10154", dmn_config=dmn_config
        )

        response = self.client.get(
            self.path, {"dmn_tabel_id": "46aa6b3a-c0a1-11e6-bc93-6ab56fad108a"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(
            response.data["resultaten"][0]["url"],
            f"{dmn_config.tabel_endpoint}/46aa6b3a-c0a1-11e6-bc93-6ab56fad108a",
        )

    def test_dmn_config_naam_filter(self):
        dmn_config = DmnConfigFactory(
            tabel_endpoint="https://gemeente-a-flowable/dmn-repository/decision-tables",
            naam="parkeervergunning opzegging",
        )
        ActieFactory.create(
            dmn_tabel_id="46aa6b3a-c0a1-11e6-bc93-6ab56fad108a",
            dmn_config=dmn_config,
        )
        ActieFactory.create(
            dmn_tabel_id="a4dcf122-e224-48f9-8c09-79e5bbb10154",
            dmn_config__naam="parkeervergunning aanvraag",
        )

        response = self.client.get(
            self.path, {"dmn_config__naam": "parkeervergunning opzegging"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(
            response.data["resultaten"][0]["url"],
            f"{dmn_config.tabel_endpoint}/46aa6b3a-c0a1-11e6-bc93-6ab56fad108a",
        )

    def test_dmn_config_naam_endpoint(self):
        dmn_config = DmnConfigFactory(
            tabel_endpoint="https://gemeente-a-flowable/dmn-repository/decision-tables"
        )
        ActieFactory.create(
            dmn_tabel_id="46aa6b3a-c0a1-11e6-bc93-6ab56fad108a",
            dmn_config=dmn_config,
        )
        ActieFactory.create(
            dmn_tabel_id="a4dcf122-e224-48f9-8c09-79e5bbb10154",
            dmn_config__tabel_endpoint="https://gemeente-b-flowable/dmn-repository/decision-tables",
        )

        response = self.client.get(
            self.path,
            {
                "dmn_config__tabel_endpoint": "https://gemeente-a-flowable/dmn-repository/decision-tables"
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(
            response.data["resultaten"][0]["url"],
            f"{dmn_config.tabel_endpoint}/46aa6b3a-c0a1-11e6-bc93-6ab56fad108a",
        )

    def test_producttype_code_filter(self):
        producttype_uuid = uuid4()
        ActieFactory.create(producttype__code="123")
        ActieFactory.create(
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
        ActieFactory.create(producttype__uuid=producttype_uuid)
        ActieFactory.create(producttype__uuid=uuid4())

        response = self.client.get(self.path + f"?producttype__uuid={producttype_uuid}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(
            response.data["resultaten"][0]["producttype_uuid"], producttype_uuid
        )

    def test_producttype_upn_filter(self):
        producttype_uuid = uuid4()
        ActieFactory.create(
            producttype__uniforme_product_naam__naam="parkeervergunning",
            producttype__uuid=producttype_uuid,
        )
        ActieFactory.create(producttype__uniforme_product_naam__naam="aanbouw")

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
        ActieFactory.create(
            producttype__naam="parkeervergunning", producttype__uuid=producttype_uuid
        )
        ActieFactory.create(producttype__naam="aanbouw")

        response = self.client.get(
            self.path, {"producttype__naam": "parkeervergunning"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(
            response.data["resultaten"][0]["producttype_uuid"], producttype_uuid
        )
