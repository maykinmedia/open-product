from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from freezegun import freeze_time

from .factories import PrijsFactory, PrijsOptieFactory, ProductTypeFactory


class TestPrijs(TestCase):

    def test_unique_validation(self):
        producttype = ProductTypeFactory.create()
        PrijsFactory.create(
            producttype=producttype, actief_vanaf=date.today() + timedelta(days=1)
        )

        with self.assertRaises(ValidationError):
            duplicate = PrijsFactory.build(
                producttype=producttype, actief_vanaf=date.today() + timedelta(days=1)
            )
            duplicate.full_clean()

    @freeze_time("2024-01-02")
    def test_min_date_validation(self):
        producttype = ProductTypeFactory.create()
        with self.assertRaises(ValidationError):
            prijs = PrijsFactory.build(
                producttype=producttype, actief_vanaf=date(2020, 1, 1)
            )
            prijs.full_clean()


class TestPrijsOptie(TestCase):
    def setUp(self):
        self.prijs = PrijsFactory.create()

    def test_min_amount_validation(self):
        with self.assertRaises(ValidationError):
            optie = PrijsOptieFactory.build(prijs=self.prijs, bedrag=Decimal("-1"))
            optie.full_clean()

    def test_decimal_place_validation(self):
        with self.assertRaises(ValidationError):
            optie = PrijsOptieFactory.build(prijs=self.prijs, bedrag=Decimal("0.001"))
            optie.full_clean()
