from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import gettext as _

from openproduct.producten.tests.factories import EigenaarFactory, ProductFactory


class TestEigenaar(TestCase):

    def test_bsn_validation_raises_on_invalid_value(self):
        invalid_values = [
            "123",  # min length
            "12345678910",  # max length
            "abcdefghi",  # regex
            "192837465",  # 11 check
        ]
        for value in invalid_values:
            with self.subTest(f"{value} should raise an error"):
                with self.assertRaises(ValidationError):
                    EigenaarFactory.create(bsn=value).full_clean()

    def test_bsn_validation_validates_on_valid_value(self):
        EigenaarFactory.create(bsn="111222333").full_clean()

    def test_kvk_validation_raises_on_invalid_value(self):
        invalid_values = [
            "1234",  # min length
            "123456789",  # max length
            "test",  # regex
        ]
        for value in invalid_values:
            with self.subTest(f"{value} should raise an error"):
                with self.assertRaises(ValidationError):
                    EigenaarFactory.build(
                        kvk_nummer=value, product=ProductFactory()
                    ).full_clean()

    def test_kvk_validation_validates_on_valid_value(self):
        EigenaarFactory.create(kvk_nummer="11122333").full_clean()

    def test_bsn_or_kvk_required(self):
        eigenaar = EigenaarFactory.create()

        with self.assertRaisesMessage(
            ValidationError,
            _(
                "Een eigenaar moet een bsn (en/of klantnummer) of een kvk nummer (met of zonder vestigingsnummer) hebben."
            ),
        ):
            eigenaar.clean()

        EigenaarFactory.create(bsn="111222333").full_clean()
        EigenaarFactory.create(klantnummer="123").full_clean()
        EigenaarFactory.create(kvk_nummer="12345678").full_clean()

    def test_vestigingsnummer_without_kvk(self):
        eigenaar = EigenaarFactory.create(vestigingsnummer="123")

        with self.assertRaisesMessage(
            ValidationError,
            _(
                "Een vestigingsnummer kan alleen in combinatie met een kvk nummer worden ingevuld."
            ),
        ):
            eigenaar.clean()

        EigenaarFactory.create(
            vestigingsnummer="123", kvk_nummer="12345678"
        ).full_clean()

    def test_identifier(self):
        expected_message = _(
            "Een eigenaar moet een bsn (en/of klantnummer) of een kvk nummer (met of zonder vestigingsnummer) hebben."
        )

        with self.subTest("bsn & kvk"):
            with self.assertRaisesMessage(ValidationError, expected_message):
                EigenaarFactory.create(bsn="111222333", kvk_nummer="12345678").clean()

        with self.subTest("klantnummer & kvk"):
            with self.assertRaisesMessage(ValidationError, expected_message):
                EigenaarFactory.create(
                    klantnummer="111222333", kvk_nummer="12345678"
                ).clean()

        with self.subTest("bsn & klantnummer"):
            EigenaarFactory.create(bsn="111222333", klantnummer="111222333").clean()

    def test_eigenaar_str(self):

        with self.subTest("bsn"):
            eigenaar = EigenaarFactory.create(bsn="111222333")
            self.assertEqual(str(eigenaar), "BSN 111222333")

        with self.subTest("klantnummer"):
            eigenaar = EigenaarFactory.create(klantnummer="123")
            self.assertEqual(str(eigenaar), "klantnummer 123")

        with self.subTest("kvk"):
            eigenaar = EigenaarFactory.create(kvk_nummer="12345678")
            self.assertEqual(str(eigenaar), "KVK 12345678")

        with self.subTest("kvk with vestigingsnummer"):
            eigenaar = EigenaarFactory.create(
                kvk_nummer="12345678", vestigingsnummer="123"
            )
            self.assertEqual(str(eigenaar), "KVK 12345678 vestigingsnummer 123")
