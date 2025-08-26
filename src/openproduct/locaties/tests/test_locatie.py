from django.test import TestCase

from .factories import LocatieFactory


class TestLocatie(TestCase):
    def test_address_no_space(self):
        locatie = LocatieFactory.create(
            straat="Keizersgracht",
            huisnummer="117",
            postcode="1015CJ",
            stad="Amsterdam",
        )
        self.assertEqual(locatie.address, "Keizersgracht 117, 1015 CJ Amsterdam")

    def test_address_with_space(self):
        locatie = LocatieFactory.create(
            straat="Keizersgracht",
            huisnummer="117",
            postcode="1015 CJ",
            stad="Amsterdam",
        )
        self.assertEqual(locatie.address, "Keizersgracht 117, 1015 CJ Amsterdam")
