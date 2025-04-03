from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from openproduct.locaties.models import Locatie
from openproduct.utils.tests.cases import BaseApiTestCase

from ..factories import LocatieFactory


class TestLocatie(BaseApiTestCase):
    path = reverse_lazy("locatie-list")

    def setUp(self):
        super().setUp()
        self.data = {"naam": "locatie", "postcode": "1111 AA", "stad": "Amsterdam"}
        self.locatie = LocatieFactory.create()

        self.detail_path = reverse("locatie-detail", args=[self.locatie.id])

    def test_read_locatie_without_credentials_returns_error(self):
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
                ]
            },
        )

    def test_create_locatie(self):
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Locatie.objects.count(), 2)

        locatie = Locatie.objects.get(id=response.data["id"])
        expected_data = {
            "id": str(locatie.id),
            "naam": locatie.naam,
            "email": locatie.email,
            "telefoonnummer": locatie.telefoonnummer,
            "straat": locatie.straat,
            "huisnummer": locatie.huisnummer,
            "postcode": locatie.postcode,
            "stad": locatie.stad,
        }
        self.assertEqual(response.data, expected_data)

    def test_update_locatie(self):
        data = self.data | {"naam": "update"}
        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Locatie.objects.count(), 1)
        self.assertEqual(Locatie.objects.get().naam, "update")

    def test_partial_update_locatie(self):
        data = {"naam": "update"}
        response = self.client.patch(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Locatie.objects.count(), 1)
        self.assertEqual(Locatie.objects.get().naam, "update")

    def test_read_locaties(self):
        locatie = LocatieFactory.create()
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        expected_data = [
            {
                "id": str(self.locatie.id),
                "naam": self.locatie.naam,
                "email": self.locatie.email,
                "telefoonnummer": self.locatie.telefoonnummer,
                "straat": self.locatie.straat,
                "huisnummer": self.locatie.huisnummer,
                "postcode": self.locatie.postcode,
                "stad": self.locatie.stad,
            },
            {
                "id": str(locatie.id),
                "naam": locatie.naam,
                "email": locatie.email,
                "telefoonnummer": locatie.telefoonnummer,
                "straat": locatie.straat,
                "huisnummer": locatie.huisnummer,
                "postcode": locatie.postcode,
                "stad": locatie.stad,
            },
        ]
        self.assertCountEqual(response.data["results"], expected_data)

    def test_read_locatie(self):
        response = self.client.get(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            "id": str(self.locatie.id),
            "naam": self.locatie.naam,
            "email": self.locatie.email,
            "telefoonnummer": self.locatie.telefoonnummer,
            "straat": self.locatie.straat,
            "huisnummer": self.locatie.huisnummer,
            "postcode": self.locatie.postcode,
            "stad": self.locatie.stad,
        }
        self.assertEqual(response.data, expected_data)

    def test_delete_locatie(self):
        response = self.client.delete(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Locatie.objects.count(), 0)
