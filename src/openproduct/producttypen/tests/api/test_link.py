from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from openproduct.producttypen.models import Link, ProductType
from openproduct.utils.tests.cases import BaseApiTestCase

from ..factories import LinkFactory, ProductTypeFactory


class TestProductTypeLink(BaseApiTestCase):
    path = reverse_lazy("link-list")

    def setUp(self):
        super().setUp()
        self.producttype = ProductTypeFactory.create()
        self.data = {
            "naam": "test link",
            "url": "https://www.google.com",
            "producttype_uuid": self.producttype.uuid,
        }
        self.link = LinkFactory.create(producttype=self.producttype)

        self.detail_path = reverse("link-detail", args=[self.link.uuid])

    def test_read_link_without_credentials_returns_error(self):
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
                "url": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
                "producttype_uuid": [
                    ErrorDetail(_("This field is required."), code="required")
                ],
            },
        )

    def test_create_link(self):
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Link.objects.count(), 2)

        response.data.pop("uuid")
        self.assertEqual(response.data, self.data)

    def test_update_link(self):
        data = self.data | {"naam": "update"}
        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Link.objects.count(), 1)
        self.assertEqual(ProductType.objects.get().links.get().naam, "update")

    def test_partial_update_link(self):
        data = {"naam": "update"}
        response = self.client.patch(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Link.objects.count(), 1)
        self.assertEqual(ProductType.objects.get().links.get().naam, "update")

    def test_read_links(self):
        link = LinkFactory.create(producttype=self.producttype)
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[_("aantal")], 2)
        expected_data = [
            {
                "uuid": str(self.link.uuid),
                "naam": self.link.naam,
                "url": self.link.url,
                "producttype_uuid": self.producttype.uuid,
            },
            {
                "uuid": str(link.uuid),
                "naam": link.naam,
                "url": link.url,
                "producttype_uuid": self.producttype.uuid,
            },
        ]
        self.assertCountEqual(response.data[_("resultaten")], expected_data)

    def test_read_link(self):
        response = self.client.get(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = {
            "uuid": str(self.link.uuid),
            "naam": self.link.naam,
            "url": self.link.url,
            "producttype_uuid": self.producttype.uuid,
        }
        self.assertEqual(response.data, expected_data)

    def test_delete_link(self):
        response = self.client.delete(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Link.objects.count(), 0)
