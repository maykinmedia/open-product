from datetime import date

from django.test import TestCase

from freezegun import freeze_time

from ...locaties.tests.factories import ContactFactory
from .factories import PrijsFactory, ProductTypeFactory


class TestProductType(TestCase):
    def setUp(self):
        self.product_type = ProductTypeFactory.create()
        self.past_prijs = PrijsFactory.create(
            product_type=self.product_type, actief_vanaf=date(2020, 1, 1)
        )
        self.current_prijs = PrijsFactory.create(
            product_type=self.product_type, actief_vanaf=date(2024, 1, 1)
        )
        self.future_prijs = PrijsFactory.create(
            product_type=self.product_type, actief_vanaf=date(2025, 1, 1)
        )

    @freeze_time("2024-02-02")
    def test_actuele_prijs_when_set(self):
        prijs = self.product_type.actuele_prijs
        self.assertEqual(prijs, self.current_prijs)

    def test_actuele_prijs_without_prijzen(self):
        self.product_type = ProductTypeFactory.create()
        self.assertIsNone(self.product_type.actuele_prijs)

    def test_clean_with_contact_that_has_no_org(self):
        contact = ContactFactory(organisatie_id=None)
        product_type = ProductTypeFactory.create()
        product_type.contacten.add(contact)
        product_type.clean()
        self.assertEqual(product_type.organisaties.count(), 0)

    def test_clean_with_contact_that_has_org(self):
        contact = ContactFactory()
        product_type = ProductTypeFactory.create()
        product_type.contacten.add(contact)
        product_type.clean()

        self.assertEqual(product_type.organisaties.count(), 1)
        self.assertEqual(product_type.organisaties.get().id, contact.organisatie.id)
