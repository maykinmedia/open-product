from datetime import date

from django.test import TestCase

from freezegun import freeze_time

from ...locaties.tests.factories import ContactFactory
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

    def test_clean_with_contact_that_has_org(self):
        contact = ContactFactory()
        producttype = ProductTypeFactory.create()
        producttype.contacten.add(contact)
        producttype.clean()

        self.assertEqual(producttype.organisaties.count(), 1)
        self.assertEqual(producttype.organisaties.get().id, contact.organisatie.id)
