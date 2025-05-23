from uuid import uuid4

from django.urls import reverse_lazy

from rest_framework import status

from openproduct.locaties.tests.factories import ContactFactory
from openproduct.utils.tests.cases import BaseApiTestCase


class TestContactFilters(BaseApiTestCase):
    path = reverse_lazy("contact-list")

    def test_rol_filter(self):
        ContactFactory.create(rol="manager")
        ContactFactory.create(rol="medewerker")

        response = self.client.get(self.path, {"rol": "manager"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["rol"], "manager")

    def test_telefoonnummer_filter(self):
        ContactFactory.create(telefoonnummer="0611223344")
        ContactFactory.create(telefoonnummer="0611223355")

        response = self.client.get(self.path, {"telefoonnummer__contains": "344"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["telefoonnummer"], "0611223344")

    def test_email_filter(self):
        ContactFactory.create(email="bob@maykinmedia.nl")
        ContactFactory.create(email="alice@maykinmedia.nl")

        response = self.client.get(self.path, {"email__iexact": "Bob@MaykinMedia.nl"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["email"], "bob@maykinmedia.nl")

    def test_achternaam_filter(self):
        ContactFactory.create(achternaam="de Vries")
        ContactFactory.create(achternaam="Jansen")

        response = self.client.get(self.path, {"achternaam": "Jansen"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["achternaam"], "Jansen")

    def test_voornaam_filter(self):
        ContactFactory.create(voornaam="Bob")
        ContactFactory.create(voornaam="Alice")

        response = self.client.get(self.path, {"voornaam": "Bob"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["voornaam"], "Bob")

    def test_organisatie_uuid_filter(self):
        org_uuid = uuid4()
        ContactFactory.create(organisatie__uuid=org_uuid)
        ContactFactory.create(organisatie__uuid=uuid4())

        response = self.client.get(self.path + f"?organisatie__uuid={org_uuid}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(
            response.data["resultaten"][0]["organisatie"]["uuid"], str(org_uuid)
        )

    def test_organisatie_naam_filter(self):
        ContactFactory.create(organisatie__naam="Maykin Media")
        ContactFactory.create(organisatie__naam="Gemeente A")

        response = self.client.get(self.path, {"organisatie__naam": "Maykin Media"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(
            response.data["resultaten"][0]["organisatie"]["naam"], "Maykin Media"
        )
