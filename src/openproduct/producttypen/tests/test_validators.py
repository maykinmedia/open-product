from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from ..models.validators import validate_producttype_code


class ValidateProductTypeCodeTest(SimpleTestCase):
    def test_valid_codes(self):
        valid_codes = [
            "ABC",
            "A1B2C3",
            "PRODUCT-001",
            "CODE-123-XYZ",
            "Z9",
        ]
        for code in valid_codes:
            try:
                validate_producttype_code(code)
            except ValidationError:
                self.fail(f"ValidationError raised for valid code: {code}")

    def test_invalid_codes(self):
        invalid_codes = {
            "abc",
            "abc-123",
            "A B C",
            "A@B#C",
            "A_B_C",
            "",
        }

        for code in invalid_codes:
            with self.assertRaises(ValidationError, msg=f"Failed on: {code}"):
                validate_producttype_code(code)
