from django.urls import reverse
from django.utils.translation import gettext as _

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from open_producten.locaties.models import Organisatie
from open_producten.utils.tests.cases import BaseApiTestCase

from ..factories import OrganisatieFactory


class TestOrganisatie(BaseApiTestCase):
    path = reverse("organisatie-list")

    def setUp(self):
        super().setUp()

        self.data = {
            "naam": "locatie",
            "code": "ORG-123",
            "postcode": "1111 AA",
            "stad": "Amsterdam",
        }
        self.organisatie = OrganisatieFactory.create()

        self.detail_path = reverse("organisatie-detail", args=[self.organisatie.id])

    def test_read_organisatie_without_credentials_returns_error(self):
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
                "code": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
            },
        )

    def test_create_organisatie(self):
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Organisatie.objects.count(), 2)
        organisatie = Organisatie.objects.get(id=response.data["id"])
        expected_data = {
            "id": str(organisatie.id),
            "naam": organisatie.naam,
            "code": organisatie.code,
            "email": organisatie.email,
            "telefoonnummer": organisatie.telefoonnummer,
            "straat": organisatie.straat,
            "huisnummer": organisatie.huisnummer,
            "postcode": organisatie.postcode,
            "stad": organisatie.stad,
        }
        self.assertEqual(response.data, expected_data)

    def test_update_organisatie(self):
        data = self.data | {"naam": "update"}
        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Organisatie.objects.count(), 1)
        self.assertEqual(Organisatie.objects.first().naam, "update")

    def test_partial_update_organisatie(self):
        data = {"naam": "update"}
        response = self.client.patch(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Organisatie.objects.count(), 1)
        self.assertEqual(Organisatie.objects.first().naam, "update")

    def test_read_organisaties(self):
        organisatie = OrganisatieFactory.create()
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        expected_data = [
            {
                "id": str(self.organisatie.id),
                "naam": self.organisatie.naam,
                "code": self.organisatie.code,
                "email": self.organisatie.email,
                "telefoonnummer": self.organisatie.telefoonnummer,
                "straat": self.organisatie.straat,
                "huisnummer": self.organisatie.huisnummer,
                "postcode": self.organisatie.postcode,
                "stad": self.organisatie.stad,
            },
            {
                "id": str(organisatie.id),
                "naam": organisatie.naam,
                "code": organisatie.code,
                "email": organisatie.email,
                "telefoonnummer": organisatie.telefoonnummer,
                "straat": organisatie.straat,
                "huisnummer": organisatie.huisnummer,
                "postcode": organisatie.postcode,
                "stad": organisatie.stad,
            },
        ]
        self.assertCountEqual(response.data["results"], expected_data)

    def test_read_organisatie(self):
        response = self.client.get(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            "id": str(self.organisatie.id),
            "naam": self.organisatie.naam,
            "code": self.organisatie.code,
            "email": self.organisatie.email,
            "telefoonnummer": self.organisatie.telefoonnummer,
            "straat": self.organisatie.straat,
            "huisnummer": self.organisatie.huisnummer,
            "postcode": self.organisatie.postcode,
            "stad": self.organisatie.stad,
        }
        self.assertEqual(response.data, expected_data)

    def test_delete_organisatie(self):
        response = self.client.delete(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Organisatie.objects.count(), 0)
