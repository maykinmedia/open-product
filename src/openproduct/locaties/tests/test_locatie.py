from django.test import TestCase

from .factories import LocatieFactory


class TestLocatie(TestCase):
    def test_address(self):
        locatie = LocatieFactory.create(
            straat="Keizersgracht",
            huisnummer="117",
            postcode="1015 CJ",
            stad="Amsterdam",
        )
        self.assertEqual(locatie.address, "Keizersgracht 117, 1015CJ Amsterdam")
