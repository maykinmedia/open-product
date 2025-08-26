from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import gettext as _

from openproduct.utils.validators import (
    validate_charfield_entry,
    validate_phone_number,
    validate_postal_code,
)


class ValidatorsTestCase(TestCase):
    """
    Validates the functions defined in ``utils.validators`` module.
    """

    def test_validate_charfield_entry_apostrophe_not_allowed(self):
        """
        Tests the ``validate_charfield_entry`` function when not explicitly
        allowing apostrophe character.
        """
        self.assertRaisesMessage(
            ValidationError,
            _("The provided value contains an invalid character: %s") % "'",
            validate_charfield_entry,
            "let's fail",
        )

    def test_validate_charfield_entry_apostrophe_allowed(self):
        """
        Tests the ``validate_charfield_entry`` function when explicitly
        allowing apostrophe character.
        """
        self.assertEqual(
            validate_charfield_entry("let's pass", allow_apostrophe=True), "let's pass"
        )

    def test_validate_postal_code(self):
        """
        Test all valid postal code and also test invalid values
        """
        invalid_postal_codes = [
            "0000AA",
            "0999AA",
            "1000  AA",
            "1000 AAA",
            "1000AAA",
            "0000aa",
            "0999aa",
            "1000  aa",
            "1000 aaa",
            "1000aaa",
            "1111,aa",
            "1111,a",
            '1111"a',
            '1111"aa',
            "1015 cj",
            "1015cj",
            "1015Cj",
            "1015cJ",
        ]
        for invalid_postal_code in invalid_postal_codes:
            self.assertRaisesMessage(
                ValidationError,
                _(
                    "Invalid postal code. A postal code must consist of 4 numbers followed by two capital letters (e.g. 1234 AB)."
                ),
                validate_postal_code,
                invalid_postal_code,
            )

        self.assertIsNone(validate_postal_code("1015 CJ"))
        self.assertIsNone(validate_postal_code("1015 AA"))

    def test_validate_phone_number(self):
        invalid_phone_numbers = [
            "0695azerty",
            "azerty0545",
            "@4566544++8",
            "onetwothreefour",
        ]
        for invalid_phone_number in invalid_phone_numbers:
            self.assertRaisesMessage(
                ValidationError,
                _("Ongeldig telefoonnummer."),
                validate_phone_number,
                invalid_phone_number,
            )

        self.assertEqual(validate_phone_number(" 0695959595"), " 0695959595")
        self.assertEqual(validate_phone_number("+33695959595"), "+33695959595")
        self.assertEqual(validate_phone_number("00695959595"), "00695959595")
        self.assertEqual(validate_phone_number("00-69-59-59-59-5"), "00-69-59-59-59-5")
        self.assertEqual(validate_phone_number("00 69 59 59 59 5"), "00 69 59 59 59 5")
