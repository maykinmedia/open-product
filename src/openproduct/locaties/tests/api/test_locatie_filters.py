from django.urls import reverse_lazy

from rest_framework import status

from openproduct.locaties.tests.factories import LocatieFactory
from openproduct.utils.tests.cases import BaseApiTestCase


class TestLocatieFilters(BaseApiTestCase):
    path = reverse_lazy("locatie-list")

    def test_naam_filter(self):
        LocatieFactory.create(naam="Maykin Media")
        LocatieFactory.create(naam="Gemeente A")

        response = self.client.get(self.path, {"naam__iexact": "Maykin Media"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["naam"], "Maykin Media")

    def test_email_filter(self):
        LocatieFactory.create(email="bob@maykinmedia.nl")
        LocatieFactory.create(email="alice@maykinmedia.nl")

        response = self.client.get(self.path, {"email__iexact": "Bob@MaykinMedia.nl"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["email"], "bob@maykinmedia.nl")

    def test_telefoonnummer_filter(self):
        LocatieFactory.create(telefoonnummer="0611223344")
        LocatieFactory.create(telefoonnummer="0611223355")

        response = self.client.get(self.path, {"telefoonnummer__contains": "344"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["telefoonnummer"], "0611223344")

    def test_straat_filter(self):
        LocatieFactory.create(straat="Kingsfortweg")
        LocatieFactory.create(straat="Queensfortweg")

        response = self.client.get(self.path, {"straat__iexact": "kingsfortweg"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["straat"], "Kingsfortweg")

    def test_huisnummer_filter(self):
        LocatieFactory.create(huisnummer="132AA")
        LocatieFactory.create(huisnummer="52")

        response = self.client.get(self.path, {"huisnummer__iexact": "132aa"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["huisnummer"], "132AA")

    def test_postcode_filter(self):
        LocatieFactory.create(postcode="1111 AA")
        LocatieFactory.create(postcode="2222 BB")

        response = self.client.get(self.path, {"postcode": "1111 AA"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["postcode"], "1111 AA")

    def test_stad_filter(self):
        LocatieFactory.create(stad="Amsterdam")
        LocatieFactory.create(stad="Zaandam")

        response = self.client.get(self.path, {"stad": "Amsterdam"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["aantal"], 1)
        self.assertEqual(response.data["resultaten"][0]["stad"], "Amsterdam")
