from datetime import date

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase

from freezegun import freeze_time

from ...locaties.tests.factories import ContactFactory
from ..models.validators import validate_producttype_code
from .factories import PrijsFactory, ProductTypeFactory


class TestProductType(TestCase):
    def setUp(self):
        self.producttype = ProductTypeFactory.create()
        self.past_prijs = PrijsFactory.create(
            producttype=self.producttype, actief_vanaf=date(2020, 1, 1)
        )
        self.current_prijs = PrijsFactory.create(
            producttype=self.producttype, actief_vanaf=date(2024, 1, 1)
        )
        self.future_prijs = PrijsFactory.create(
            producttype=self.producttype, actief_vanaf=date(2025, 1, 1)
        )

    @freeze_time("2024-02-02")
    def test_actuele_prijs_when_set(self):
        prijs = self.producttype.actuele_prijs
        self.assertEqual(prijs, self.current_prijs)

    def test_actuele_prijs_without_prijzen(self):
        self.producttype = ProductTypeFactory.create()
        self.assertIsNone(self.producttype.actuele_prijs)

    def test_clean_with_contact_that_has_no_org(self):
        contact = ContactFactory(organisatie_id=None)
        producttype = ProductTypeFactory.create()
        producttype.contacten.add(contact)
        producttype.clean()
        self.assertEqual(producttype.organisaties.count(), 0)

    def test_save_with_contact_that_has_org(self):
        contact = ContactFactory()
        producttype = ProductTypeFactory.create()
        producttype.contacten.add(contact)
        producttype.save()

        self.assertEqual(producttype.organisaties.count(), 1)
        self.assertEqual(producttype.organisaties.get().id, contact.organisatie.id)


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
        invalid_codes = [
            "abc",
            "abc-123",
            "A B C",
            "A@B#C",
            "A_B_C",
        ]

        for code in invalid_codes:
            with self.assertRaises(ValidationError, msg=f"Failed on: {code}"):
                validate_producttype_code(code)
