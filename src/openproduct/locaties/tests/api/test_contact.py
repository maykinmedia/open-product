from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient

from openproduct.locaties.models import Contact
from openproduct.utils.tests.cases import BaseApiTestCase

from ..factories import ContactFactory, OrganisatieFactory


class TestContact(BaseApiTestCase):
    path = reverse_lazy("contact-list")

    def setUp(self):
        super().setUp()
        organisatie = OrganisatieFactory.create()
        self.data = {
            "voornaam": "bob",
            "achternaam": "de vries",
            "organisatie_id": organisatie.id,
        }
        self.contact = ContactFactory.create()

        self.detail_path = reverse("contact-detail", args=[self.contact.id])

    def test_read_contact_without_credentials_returns_error(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_required_fields(self):
        response = self.client.post(self.path, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "voornaam": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
                "achternaam": [
                    ErrorDetail(string=_("This field is required."), code="required")
                ],
            },
        )

    def test_create_contact(self):
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Contact.objects.count(), 2)

        contact = Contact.objects.get(id=response.data["id"])
        expected_data = {
            "id": str(contact.id),
            "voornaam": contact.voornaam,
            "achternaam": contact.achternaam,
            "email": contact.email,
            "telefoonnummer": contact.telefoonnummer,
            "rol": "",
            "organisatie": {
                "id": str(contact.organisatie.id),
                "naam": contact.organisatie.naam,
                "code": contact.organisatie.code,
                "email": contact.organisatie.email,
                "telefoonnummer": contact.organisatie.telefoonnummer,
                "straat": contact.organisatie.straat,
                "huisnummer": contact.organisatie.huisnummer,
                "postcode": contact.organisatie.postcode,
                "stad": contact.organisatie.stad,
            },
        }
        self.assertEqual(response.data, expected_data)

    def test_update_contact(self):
        data = self.data | {"voornaam": "update"}
        response = self.client.put(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Contact.objects.count(), 1)
        self.assertEqual(Contact.objects.get().voornaam, "update")

    def test_partial_update_contact(self):
        data = {"voornaam": "update"}
        response = self.client.patch(self.detail_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Contact.objects.count(), 1)
        self.assertEqual(Contact.objects.get().voornaam, "update")

    def test_read_contacten(self):
        contact = ContactFactory.create()
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        expected_data = [
            {
                "id": str(self.contact.id),
                "voornaam": self.contact.voornaam,
                "achternaam": self.contact.achternaam,
                "email": self.contact.email,
                "telefoonnummer": self.contact.telefoonnummer,
                "rol": self.contact.rol,
                "organisatie": {
                    "id": str(self.contact.organisatie.id),
                    "naam": self.contact.organisatie.naam,
                    "code": self.contact.organisatie.code,
                    "email": self.contact.organisatie.email,
                    "telefoonnummer": self.contact.organisatie.telefoonnummer,
                    "straat": self.contact.organisatie.straat,
                    "huisnummer": self.contact.organisatie.huisnummer,
                    "postcode": self.contact.organisatie.postcode,
                    "stad": self.contact.organisatie.stad,
                },
            },
            {
                "id": str(contact.id),
                "voornaam": contact.voornaam,
                "achternaam": contact.achternaam,
                "email": contact.email,
                "telefoonnummer": contact.telefoonnummer,
                "rol": contact.rol,
                "organisatie": {
                    "id": str(contact.organisatie.id),
                    "naam": contact.organisatie.naam,
                    "code": contact.organisatie.code,
                    "email": contact.organisatie.email,
                    "telefoonnummer": contact.organisatie.telefoonnummer,
                    "straat": contact.organisatie.straat,
                    "huisnummer": contact.organisatie.huisnummer,
                    "postcode": contact.organisatie.postcode,
                    "stad": contact.organisatie.stad,
                },
            },
        ]
        self.assertCountEqual(response.data["results"], expected_data)

    def test_read_contact(self):
        response = self.client.get(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            "id": str(self.contact.id),
            "voornaam": self.contact.voornaam,
            "achternaam": self.contact.achternaam,
            "email": self.contact.email,
            "telefoonnummer": self.contact.telefoonnummer,
            "rol": self.contact.rol,
            "organisatie": {
                "id": str(self.contact.organisatie.id),
                "naam": self.contact.organisatie.naam,
                "code": self.contact.organisatie.code,
                "email": self.contact.organisatie.email,
                "telefoonnummer": self.contact.organisatie.telefoonnummer,
                "straat": self.contact.organisatie.straat,
                "huisnummer": self.contact.organisatie.huisnummer,
                "postcode": self.contact.organisatie.postcode,
                "stad": self.contact.organisatie.stad,
            },
        }
        self.assertEqual(response.data, expected_data)

    def test_delete_contact(self):
        response = self.client.delete(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Contact.objects.count(), 0)
