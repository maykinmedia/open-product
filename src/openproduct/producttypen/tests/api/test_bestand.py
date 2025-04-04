import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from openproduct.producttypen.models import Bestand
from openproduct.utils.tests.cases import BaseApiTestCase

from ..factories import BestandFactory, ProductTypeFactory

TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestProductTypeBestand(BaseApiTestCase):
    path = reverse_lazy("bestand-list")

    def setUp(self):
        super().setUp()
        self.product_type = ProductTypeFactory.create()
        self.data = {
            "product_type_id": self.product_type.id,
            "bestand": SimpleUploadedFile(
                "test.txt", b"test content.", content_type="text/plain"
            ),
        }
        self.bestand = BestandFactory.create(product_type=self.product_type)

        self.detail_path = reverse("bestand-detail", args=[self.bestand.id])

    def test_read_bestand_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_required_fields(self):
        response = self.client.post(self.path, {}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "bestand": [
                    ErrorDetail(
                        string=_("Er is geen bestand opgestuurd."), code="required"
                    )
                ],
                "product_type_id": [
                    ErrorDetail(_("This field is required."), code="required")
                ],
            },
        )

    def test_create_bestand(self):
        response = self.client.post(self.path, self.data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Bestand.objects.count(), 2)

        id = response.data.pop("id")
        self.assertEqual(response.data["product_type_id"], self.product_type.id)

        bestand_url = response.data["bestand"]

        self.assertRegex(bestand_url, r"http://testserver/media/test.*\.txt")

        self.assertEqual(
            Bestand.objects.get(id=id).bestand.file.readline(), b"test content."
        )

    def test_update_bestand_product_type_id(self):
        product_type = ProductTypeFactory.create()
        data = self.data | {"product_type_id": product_type.id}
        response = self.client.put(self.detail_path, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Bestand.objects.count(), 1)
        self.assertEqual(Bestand.objects.get().product_type, product_type)

    def test_update_bestand_file(self):
        data = self.data | {
            "bestand": SimpleUploadedFile(
                "456.txt", b"456 content.", content_type="text/plain"
            )
        }
        response = self.client.put(self.detail_path, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Bestand.objects.count(), 1)
        self.assertEqual(Bestand.objects.get().bestand.url, "/media/456.txt")
        self.assertEqual(Bestand.objects.get().bestand.file.readline(), b"456 content.")

    def test_partial_update_bestand_product_type_id(self):
        product_type = ProductTypeFactory.create()
        data = {"product_type_id": product_type.id}
        response = self.client.patch(self.detail_path, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Bestand.objects.count(), 1)
        self.assertEqual(Bestand.objects.get().product_type, product_type)

    def test_partial_update_bestand_file(self):
        data = {
            "bestand": SimpleUploadedFile(
                "123.txt", b"123 content.", content_type="text/plain"
            )
        }
        response = self.client.patch(self.detail_path, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Bestand.objects.count(), 1)
        self.assertEqual(Bestand.objects.get().bestand.url, "/media/123.txt")
        self.assertEqual(Bestand.objects.get().bestand.file.readline(), b"123 content.")

    def test_read_bestanden(self):
        bestand = BestandFactory.create(product_type=self.product_type)
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        expected_data = [
            {
                "id": str(self.bestand.id),
                "bestand": "http://testserver" + self.bestand.bestand.url,
                "product_type_id": self.product_type.id,
            },
            {
                "id": str(bestand.id),
                "bestand": "http://testserver" + bestand.bestand.url,
                "product_type_id": self.product_type.id,
            },
        ]
        self.assertCountEqual(response.data["results"], expected_data)

    def test_read_bestand(self):
        response = self.client.get(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = {
            "id": str(self.bestand.id),
            "bestand": "http://testserver" + self.bestand.bestand.url,
            "product_type_id": self.product_type.id,
        }
        self.assertEqual(response.data, expected_data)

    def test_delete_bestand(self):
        response = self.client.delete(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Bestand.objects.count(), 0)
