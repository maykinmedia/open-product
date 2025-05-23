from django.urls import reverse_lazy

from rest_framework import status

from openproduct.locaties.tests.factories import OrganisatieFactory
from openproduct.utils.tests.cases import BaseApiTestCase


class TestOrganisatieFilters(BaseApiTestCase):
    path = reverse_lazy("organisatie-list")

    def test_naam_filter(self):
        OrganisatieFactory.create(naam="Maykin Media")
        OrganisatieFactory.create(naam="Gemeente A")

        response = self.client.get(self.path, {"naam__iexact": "Maykin Media"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["naam"], "Maykin Media")

    def test_email_filter(self):
        OrganisatieFactory.create(email="bob@maykinmedia.nl")
        OrganisatieFactory.create(email="alice@maykinmedia.nl")

        response = self.client.get(self.path, {"email__iexact": "Bob@MaykinMedia.nl"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["email"], "bob@maykinmedia.nl")

    def test_telefoonnummer_filter(self):
        OrganisatieFactory.create(telefoonnummer="0611223344")
        OrganisatieFactory.create(telefoonnummer="0611223355")

        response = self.client.get(self.path, {"telefoonnummer__contains": "344"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["telefoonnummer"], "0611223344")

    def test_straat_filter(self):
        OrganisatieFactory.create(straat="Kingsfortweg")
        OrganisatieFactory.create(straat="Queensfortweg")

        response = self.client.get(self.path, {"straat__iexact": "kingsfortweg"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["straat"], "Kingsfortweg")

    def test_huisnummer_filter(self):
        OrganisatieFactory.create(huisnummer="132AA")
        OrganisatieFactory.create(huisnummer="52")

        response = self.client.get(self.path, {"huisnummer__iexact": "132aa"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["huisnummer"], "132AA")

    def test_postcode_filter(self):
        OrganisatieFactory.create(postcode="1111 AA")
        OrganisatieFactory.create(postcode="2222 BB")

        response = self.client.get(self.path, {"postcode": "1111 AA"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["postcode"], "1111 AA")

    def test_stad_filter(self):
        OrganisatieFactory.create(stad="Amsterdam")
        OrganisatieFactory.create(stad="Zaandam")

        response = self.client.get(self.path, {"stad": "Amsterdam"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["stad"], "Amsterdam")

    def test_code_filter(self):
        OrganisatieFactory.create(code="123")
        OrganisatieFactory.create(code="8q30298472019387409")

        response = self.client.get(self.path, {"code": "8q30298472019387409"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["code"], "8q30298472019387409")
