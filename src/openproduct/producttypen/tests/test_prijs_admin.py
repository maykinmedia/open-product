from datetime import date

from django.contrib.admin import AdminSite
from django.test import TestCase
from django.utils.translation import gettext as _

from freezegun import freeze_time

from openproduct.accounts.tests.factories import UserFactory
from openproduct.producttypen.admin import PrijsAdmin
from openproduct.producttypen.admin.prijs import PrijsAdminForm
from openproduct.producttypen.models import Prijs
from openproduct.producttypen.tests.factories import PrijsFactory, ProductTypeFactory


@freeze_time("2024-01-02")
class TestPrijsAdmin(TestCase):

    def setUp(self):
        producttype = ProductTypeFactory.create()
        self.data = {
            "producttype": producttype.id,
            "actief_vanaf": "2025-01-01",
            "prijsregels-TOTAL_FORMS": "1",
            "prijsregels-INITIAL_FORMS": "0",
            "prijsregels-0-dmn_tabel_id": "",
            "prijsopties-TOTAL_FORMS": "1",
            "prijsopties-INITIAL_FORMS": "0",
            "prijsopties-0-bedrag": "",
        }

    def test_change_permission_on_old_price(self):
        instance = PrijsFactory.create(actief_vanaf=date(2024, 1, 1))
        admin = PrijsAdmin(Prijs, AdminSite())
        request = self.client.request()
        request.user = UserFactory(superuser=True)

        self.assertFalse(admin.has_change_permission(request, instance))

    def test_change_permission_on_future_price(self):
        instance = PrijsFactory.create(actief_vanaf=date(2024, 3, 1))
        admin = PrijsAdmin(Prijs, AdminSite())
        request = self.client.request()
        request.user = UserFactory(superuser=True)

        self.assertTrue(admin.has_change_permission(request, instance))

    def test_change_permission_on_current_price(self):
        instance = PrijsFactory.create(actief_vanaf=date(2024, 1, 2))
        admin = PrijsAdmin(Prijs, AdminSite())
        request = self.client.request()
        request.user = UserFactory(superuser=True)

        self.assertTrue(admin.has_change_permission(request, instance))

    def test_prijs_needs_to_have_optie_or_regel(self):
        form = PrijsAdminForm(data=self.data)

        self.assertEqual(
            form.errors,
            {"__all__": [_("Een prijs moet één of meerdere opties of regels hebben.")]},
        )

    def test_prijs_cannot_have_optie_and_regel(self):
        data = self.data | {
            "prijsregels-0-dmn_tabel_id": "809e1b4b-b027-42b6-a5df-2d3156e8c032",
            "prijsopties-0-bedrag": "10",
        }
        form = PrijsAdminForm(data=data)

        self.assertEqual(
            form.errors,
            {"__all__": [_("Een prijs kan niet zowel opties als regels hebben.")]},
        )

    def test_prijs_deleting_only_regel(self):
        data = self.data | {
            "prijsregels-0-dmn_tabel_id": "809e1b4b-b027-42b6-a5df-2d3156e8c032",
            "prijsregels-0-DELETE": "on",
        }
        form = PrijsAdminForm(data=data)

        self.assertEqual(
            form.errors,
            {"__all__": [_("Een prijs moet één of meerdere opties of regels hebben.")]},
        )

    def test_prijs_deleting_only_optie(self):
        data = self.data | {
            "prijsopties-0-bedrag": "10",
            "prijsopties-0-DELETE": "on",
        }
        form = PrijsAdminForm(data=data)

        self.assertEqual(
            form.errors,
            {"__all__": [_("Een prijs moet één of meerdere opties of regels hebben.")]},
        )

    def test_prijs_removing_optie_adding_regel(self):
        data = self.data | {
            "prijsregels-0-dmn_tabel_id": "809e1b4b-b027-42b6-a5df-2d3156e8c032",
            "prijsopties-0-bedrag": "10",
            "prijsopties-0-DELETE": "on",
        }
        form = PrijsAdminForm(data=data)

        self.assertEqual(form.errors, {})

    def test_prijs_removing_regel_adding_optie(self):
        data = self.data | {
            "prijsregels-0-dmn_tabel_id": "809e1b4b-b027-42b6-a5df-2d3156e8c032",
            "prijsregels-0-DELETE": "on",
            "prijsopties-0-bedrag": "10",
        }
        form = PrijsAdminForm(data=data)

        self.assertEqual(form.errors, {})
