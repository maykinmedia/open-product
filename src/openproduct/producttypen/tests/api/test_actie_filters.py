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
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["naam"], "verlegging")

    def test_naam_contains_filter(self):
        ActieFactory.create(naam="verlegging")
        ActieFactory.create(naam="opzegging")

        response = self.client.get(self.path, {"naam__contains": "opzeg"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["naam"], "opzegging")

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
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["url"],
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
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["url"],
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
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["url"],
            f"{dmn_config.tabel_endpoint}/46aa6b3a-c0a1-11e6-bc93-6ab56fad108a",
        )

    def test_product_type_code_filter(self):
        product_type_id = uuid4()
        ActieFactory.create(product_type__code="123")
        ActieFactory.create(
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
        ActieFactory.create(product_type__id=product_type_id)
        ActieFactory.create(product_type__id=uuid4())

        response = self.client.get(self.path + f"?product_type__id={product_type_id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["product_type_id"], product_type_id
        )

    def test_product_type_upn_filter(self):
        product_type_id = uuid4()
        ActieFactory.create(
            product_type__uniforme_product_naam__naam="parkeervergunning",
            product_type__id=product_type_id,
        )
        ActieFactory.create(product_type__uniforme_product_naam__naam="aanbouw")

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
        ActieFactory.create(
            product_type__naam="parkeervergunning", product_type__id=product_type_id
        )
        ActieFactory.create(product_type__naam="aanbouw")

        response = self.client.get(
            self.path, {"product_type__naam": "parkeervergunning"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["product_type_id"], product_type_id
        )
