from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from openproduct.producttypen.models import Actie, ProductType
from openproduct.utils.tests.cases import BaseApiTestCase

from ..factories import ActieFactory, ProductTypeFactory


class TestProductTypeActie(BaseApiTestCase):
    path = reverse_lazy("actie-list")

    def setUp(self):
        super().setUp()
        self.producttype = ProductTypeFactory.create()
        self.data = {
            "naam": "test actie",
            "tabel_endpoint": "https://gemeente-a-flowable/dmn-repository/decision-tables",
            "dmn_tabel_id": "46aa6b3a-c0a1-11e6-bc93-6ab56fad108a",
            "producttype_uuid": self.producttype.uuid,
        }
        self.actie = ActieFactory.create(
            producttype=self.producttype,
            dmn_config__tabel_endpoint="https://gemeente-a-flowable/dmn-repository/decision-tables",
        )

        self.detail_path = reverse("actie-detail", args=[self.actie.uuid])

    def test_read_actie_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_required_fields(self):
        response = self.client.post(self.path, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "naam": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
                "tabel_endpoint": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
                "producttype_uuid": [
                    ErrorDetail(_("This field is required."), code="required")
                ],
                "dmn_tabel_id": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
            },
        )

    def test_create_actie(self):
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Actie.objects.count(), 2)

        response.data.pop("uuid")

        self.assertEqual(
            response.data,
            {
                "naam": self.data["naam"],
                "producttype_uuid": self.data["producttype_uuid"],
                "url": f"{self.data['tabel_endpoint']}/{self.data['dmn_tabel_id']}",
                "mapping": None,
            },
        )

    def test_create_actie_with_invalid_mapping(self):
        data = self.data | {
            "mapping": {"code": "abc", "test": "123"},
        }

        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "mapping": [
                    ErrorDetail(
                        string=_(
                            "De mapping komt niet overeen met het schema. (zie API spec)"
                        ),
                        code="invalid",
                    )
                ]
            },
        )

    def test_create_actie_with_valid_mapping(self):
        data = self.data | {
            "mapping": {
                "product": [
                    {
                        "name": "status",
                        "classType": "String",
                        "regex": "$.status",
                    }
                ]
            }
        }

        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["mapping"],
            {
                "product": [
                    {"name": "status", "classType": "String", "regex": "$.status"}
                ]
            },
        )

    def test_update_actie(self):
        data = self.data | {"naam": "update"}
        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Actie.objects.count(), 1)
        self.assertEqual(ProductType.objects.get().acties.get().naam, "update")

    def test_partial_update_actie(self):
        data = {"naam": "update"}
        response = self.client.patch(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Actie.objects.count(), 1)
        self.assertEqual(ProductType.objects.get().acties.get().naam, "update")

    def test_read_acties(self):
        actie = ActieFactory.create(producttype=self.producttype)
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        expected_data = [
            {
                "uuid": str(self.actie.uuid),
                "naam": self.actie.naam,
                "url": self.actie.url,
                "producttype_uuid": self.producttype.uuid,
                "mapping": self.actie.mapping,
            },
            {
                "uuid": str(actie.uuid),
                "naam": actie.naam,
                "url": actie.url,
                "producttype_uuid": self.producttype.uuid,
                "mapping": self.actie.mapping,
            },
        ]
        self.assertCountEqual(response.data["results"], expected_data)

    def test_read_actie(self):
        response = self.client.get(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = {
            "uuid": str(self.actie.uuid),
            "naam": self.actie.naam,
            "url": self.actie.url,
            "producttype_uuid": self.producttype.uuid,
            "mapping": self.actie.mapping,
        }
        self.assertEqual(response.data, expected_data)

    def test_delete_actie(self):
        response = self.client.delete(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Actie.objects.count(), 0)
