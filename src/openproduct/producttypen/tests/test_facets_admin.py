from django.test import TestCase, tag
from django.urls import reverse
from django.utils.translation import gettext as _

from maykin_2fa.test import disable_admin_mfa
from playwright.sync_api import expect

from openproduct.accounts.tests.factories import UserFactory
from openproduct.utils.tests.e2e import DEFAULT_PASSWORD, E2ETestCase

from ...producttypen.tests.factories import ProductTypeFactory
from ..models import FacetType, FacetWaarde
from .factories import FacetTypeFactory, FacetWaardeFactory


class TestFacetTypeAdmin(TestCase):
    add_url = reverse("admin:producttypen_facettype_add")
    changelist_url = reverse("admin:producttypen_facettype_changelist")

    def setUp(self):
        self.user = UserFactory.create(superuser=True)
        self.client.force_login(self.user)

        self.data = {
            "naam": "doelgroep",
            "omschrijving": "",
            "waarden-TOTAL_FORMS": "0",
            "waarden-INITIAL_FORMS": "0",
            "waarden-MIN_NUM_FORMS": "0",
            "waarden-MAX_NUM_FORMS": "1000",
        }

    def _change_url(self, instance):
        return reverse("admin:producttypen_facettype_change", args=[instance.pk])

    def test_changelist_loads(self):
        FacetTypeFactory.create(naam="doelgroep")

        response = self.client.get(self.changelist_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "doelgroep")

    def test_create_facettype_without_waarden(self):
        response = self.client.post(self.add_url, self.data)

        self.assertEqual(response.status_code, 302)
        facet_type = FacetType.objects.get()
        self.assertEqual(facet_type.naam, "doelgroep")
        self.assertFalse(facet_type.facetteerbaar)
        self.assertFalse(facet_type.meervoudig_toegestaan)
        self.assertFalse(facet_type.verplicht)
        self.assertEqual(facet_type.waarden.count(), 0)

    def test_create_facettype_with_booleans(self):
        data = self.data | {
            "facetteerbaar": "on",
            "meervoudig_toegestaan": "on",
            "verplicht": "on",
        }

        response = self.client.post(self.add_url, data)

        self.assertEqual(response.status_code, 302)
        facet_type = FacetType.objects.get()
        self.assertTrue(facet_type.facetteerbaar)
        self.assertTrue(facet_type.meervoudig_toegestaan)
        self.assertTrue(facet_type.verplicht)

    def test_create_facettype_with_waarden(self):
        data = self.data | {
            "waarden-TOTAL_FORMS": "2",
            "waarden-0-naam": "inwoners",
            "waarden-0-actief": "on",
            "waarden-1-naam": "bedrijven",
        }

        response = self.client.post(self.add_url, data)

        self.assertEqual(response.status_code, 302)
        facet_type = FacetType.objects.get()
        self.assertEqual(
            list(facet_type.waarden.values_list("naam", "actief")),
            [("bedrijven", False), ("inwoners", True)],
        )

    def test_create_facettype_without_naam(self):
        data = self.data | {"naam": ""}

        response = self.client.post(self.add_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["adminform"].form.errors,
            {"naam": [_("This field is required.")]},
        )
        self.assertFalse(FacetType.objects.exists())

    def test_create_waarde_without_naam(self):
        data = self.data | {
            "waarden-TOTAL_FORMS": "1",
            "waarden-0-omschrijving": "zonder naam",
        }

        response = self.client.post(self.add_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["inline_admin_formsets"][0].formset.errors,
            [{"naam": [_("This field is required.")]}],
        )
        self.assertFalse(FacetType.objects.exists())

    # Change

    def test_add_waarde_to_existing_facettype(self):
        facet_type = FacetTypeFactory.create(naam="doelgroep")
        data = self.data | {
            "waarden-TOTAL_FORMS": "1",
            "waarden-0-naam": "inwoners",
            "waarden-0-actief": "on",
        }

        url = reverse("admin:producttypen_facettype_change", args=[facet_type.pk])
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(facet_type.waarden.get().naam, "inwoners")

    def test_update_existing_waarde(self):
        facet_type = FacetTypeFactory.create(naam="doelgroep")
        waarde = FacetWaardeFactory.create(
            facet_type=facet_type, naam="inwoners", actief=True
        )
        data = self.data | {
            "waarden-TOTAL_FORMS": "1",
            "waarden-INITIAL_FORMS": "1",
            "waarden-0-id": str(waarde.pk),
            "waarden-0-facet_type": str(facet_type.pk),
            "waarden-0-naam": "burgers",
        }

        url = reverse("admin:producttypen_facettype_change", args=[facet_type.pk])
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        waarde.refresh_from_db()
        self.assertEqual(waarde.naam, "burgers")
        self.assertFalse(waarde.actief)

    def test_delete_waarde_via_inline(self):
        facet_type = FacetTypeFactory.create(naam="doelgroep")
        waarde = FacetWaardeFactory.create(facet_type=facet_type, naam="inwoners")
        data = self.data | {
            "waarden-TOTAL_FORMS": "1",
            "waarden-INITIAL_FORMS": "1",
            "waarden-0-id": str(waarde.pk),
            "waarden-0-facet_type": str(facet_type.pk),
            "waarden-0-naam": "inwoners",
            "waarden-0-DELETE": "on",
        }

        url = reverse("admin:producttypen_facettype_change", args=[facet_type.pk])
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(FacetWaarde.objects.exists())


@tag("playwright")
@disable_admin_mfa()
class TestProductTypeFacettenAdmin(E2ETestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory.create(superuser=True, password=DEFAULT_PASSWORD)
        self.producttype = ProductTypeFactory.create(themas=1)
        self.url = self.live_reverse(
            "admin:producttypen_producttype_change", args=[self.producttype.pk]
        )

    def _row(self, page, index):
        return (
            page.locator(f"#id_ProductType_facetten-{index}-facet_type"),
            page.locator(f"#id_ProductType_facetten-{index}-facetwaarde"),
        )

    def _real_options(self, select):
        return select.locator("option:not([value=''])")

    def _option_values(self, select):
        return select.locator("option:not([value=''])").evaluate_all(
            "opts => opts.map(o => o.value)"
        )

    def _save(self, page):
        page.click("input[name=_save]")

    def test_add_valid_facetwaarde(self):
        facet_type_obj = FacetTypeFactory.create(waarden=1)
        FacetTypeFactory.create(waarden=3)
        facet_waarde_obj = facet_type_obj.waarden.first()

        page = self.new_page(self.user)
        page.goto(self.url)

        facet_type, facet_waarde = self._row(page, 0)
        facet_type.select_option(str(facet_type_obj.pk))
        expected = [
            str(pk) for pk in facet_type_obj.waarden.values_list("pk", flat=True)
        ]
        expect(self._real_options(facet_waarde)).to_have_count(len(expected))
        facet_waarde.select_option(str(facet_waarde_obj.pk))

        self.assertCountEqual(self._option_values(facet_waarde), expected)

        self._save(page)
        self.assertEqual(list(self.producttype.facetten.all()), [facet_waarde_obj])

    def test_changing_facet_type_updates_facetwaarde_options(self):
        facet_type_a = FacetTypeFactory.create(waarden=1)
        facet_type_b = FacetTypeFactory.create(waarden=3)
        facet_waarde_a = facet_type_a.waarden.first()

        page = self.new_page(self.user)
        page.goto(self.url)

        facet_type, facet_waarde = self._row(page, 0)
        # first select
        facet_type.select_option(str(facet_type_a.pk))
        expect(
            facet_waarde.locator(f"option[value='{facet_waarde_a.pk}']")
        ).to_be_attached()
        facet_waarde.select_option(str(facet_waarde_a.pk))

        # second select
        facet_type.select_option(str(facet_type_b.pk))

        expect(self._real_options(facet_waarde)).to_have_count(3)
        expect(
            facet_waarde.locator(f"option[value='{facet_waarde_a.pk}']")
        ).to_have_count(0)

        expect(facet_waarde).not_to_have_value(str(facet_waarde_a.pk))

    def test_no_facet_type_selected_has_no_facetwaarde_options(self):
        FacetTypeFactory.create(waarden=3)

        page = self.new_page(self.user)
        page.goto(self.url)

        facet_type, facet_waarde = self._row(page, 0)
        expect(self._real_options(facet_waarde)).to_have_count(0)

    def test_facetwaarde_of_other_type_invalid(self):
        facet_type_obj_1 = FacetTypeFactory.create(waarden=1)
        facet_type_obj_2 = FacetTypeFactory.create(waarden=1)
        facet_waarde = facet_type_obj_2.waarden.first()

        page = self.new_page(self.user)
        page.goto(self.url)

        facet_type, facet_waarde = self._row(page, 0)
        facet_type.select_option(str(facet_type_obj_1.pk))
        expect(self._real_options(facet_waarde)).to_have_count(1)

        self._save(page)

        expect(page.locator(".errornote")).to_be_visible()
        self.assertFalse(self.producttype.facetten.exists())

    def test_validate_verplichte_facetten(self):
        facet_type_obj_1 = FacetTypeFactory.create(waarden=1, verplicht=True)
        facet_type_obj_2 = FacetTypeFactory.create(waarden=1, verplicht=False)

        facet_waarde_obj = facet_type_obj_1.waarden.first()

        page = self.new_page(self.user)
        page.goto(self.url)

        # select only for facet_type_obj_1
        facet_type, facet_waarde = self._row(page, 0)
        facet_type.select_option(str(facet_type_obj_1.pk))
        facet_waarde.select_option(str(facet_waarde_obj.pk))

        self._save(page)
        self.assertEqual(list(self.producttype.facetten.all()), [facet_waarde_obj])

        facet_type_obj_2.verplicht = True
        facet_type_obj_2.save()

        # just save producttype
        page = self.new_page(self.user)
        page.goto(self.url)
        self._save(page)
        expect(page.locator(".errornote")).to_be_visible()

        expect(
            page.locator("#ProductType_facetten-group .errorlist.nonform")
        ).to_contain_text("Verplichte facettypes ontbreken: facettype 1.")

        # select only for facet_type_obj_2
        facet_type, facet_waarde = self._row(page, 1)
        facet_waarde_obj = facet_type_obj_2.waarden.first()
        facet_type.select_option(str(facet_type_obj_2.pk))
        facet_waarde.select_option(str(facet_waarde_obj.pk))

        self._save(page)
        self.assertEqual(self.producttype.facetten.count(), 2)

    def test_validate_meervoudig_facetten(self):
        with self.subTest("multiple == True"):
            facet_type_obj = FacetTypeFactory.create(
                waarden=2, meervoudig_toegestaan=True
            )

            facet_waarde_1 = facet_type_obj.waarden.all()[0]
            facet_waarde_2 = facet_type_obj.waarden.all()[1]

            page = self.new_page(self.user)
            page.goto(self.url)

            # select only for facet_type_obj
            facet_type, facet_waarde = self._row(page, 0)
            facet_type.select_option(str(facet_type_obj.pk))
            facet_waarde.select_option(str(facet_waarde_1.pk))

            page.get_by_role(
                "button", name="Nog een Producttype-facetwaarde-relatie toevoegen"
            ).click()

            facet_type, facet_waarde = self._row(page, 1)
            facet_type.select_option(str(facet_type_obj.pk))
            facet_waarde.select_option(str(facet_waarde_2.pk))

            self._save(page)

            self.assertEqual(self.producttype.facetten.count(), 2)

        with self.subTest("multiple == False"):
            facet_type_obj = FacetTypeFactory.create(
                waarden=2, meervoudig_toegestaan=False
            )

            facet_waarde_1 = facet_type_obj.waarden.all()[0]
            facet_waarde_2 = facet_type_obj.waarden.all()[1]

            page = self.new_page(self.user)
            page.goto(self.url)

            # select only for facet_type_obj
            facet_type, facet_waarde = self._row(page, 2)
            facet_type.select_option(str(facet_type_obj.pk))
            facet_waarde.select_option(str(facet_waarde_1.pk))

            page.get_by_role(
                "button", name="Nog een Producttype-facetwaarde-relatie toevoegen"
            ).click()

            facet_type, facet_waarde = self._row(page, 3)
            facet_type.select_option(str(facet_type_obj.pk))
            facet_waarde.select_option(str(facet_waarde_2.pk))

            self._save(page)

            expect(
                page.locator("#ProductType_facetten-group .errorlist.nonform")
            ).to_contain_text(
                "Facettype 'facettype 1' staat maar één waarde toe, gekregen: facetwaarde 2, facetwaarde 3.",
            )

            self.assertEqual(self.producttype.facetten.count(), 2)

            # reload the page and select only one
            page = self.new_page(self.user)
            page.goto(self.url)

            facet_type, facet_waarde = self._row(page, 2)
            facet_type.select_option(str(facet_type_obj.pk))
            facet_waarde.select_option(str(facet_waarde_1.pk))

            self._save(page)
            # total for the same producttype ==  3
            self.assertEqual(self.producttype.facetten.count(), 3)

    def test_check_meervoudig_facettype(self):
        # facet_type_obj.meervoudig_toegestaan == True
        # producttype has multiple facetten

        facet_type_obj = FacetTypeFactory.create(waarden=2, meervoudig_toegestaan=True)
        self.producttype.facetten.add(*facet_type_obj.waarden.all())

        page = self.new_page(self.user)
        page.goto(
            self.live_reverse(
                "admin:producttypen_facettype_change", args=[facet_type_obj.pk]
            )
        )

        checkbox = page.locator("#id_meervoudig_toegestaan")
        expect(checkbox).to_be_checked()
        checkbox.uncheck()

        self._save(page)

        expect(page.locator(".errornote")).to_be_visible()
        expect(page.locator(".field-meervoudig_toegestaan .errorlist")).to_contain_text(
            "Kan niet uitgezet worden: er zijn producttypen met meerdere waarden van dit facet."
        )
        facet_type_obj.refresh_from_db()
        self.assertTrue(facet_type_obj.meervoudig_toegestaan)

        # producttype has only one facet
        facet_type_obj = FacetTypeFactory.create(waarden=1, meervoudig_toegestaan=True)
        self.producttype.facetten.add(*facet_type_obj.waarden.all())

        page = self.new_page(self.user)
        page.goto(
            self.live_reverse(
                "admin:producttypen_facettype_change", args=[facet_type_obj.pk]
            )
        )

        checkbox = page.locator("#id_meervoudig_toegestaan")
        expect(checkbox).to_be_checked()
        checkbox.uncheck()

        self._save(page)

        expect(page.locator(".messagelist .success")).to_be_visible()
        expect(page.locator(".errornote")).to_have_count(0)
        facet_type_obj.refresh_from_db()
        self.assertFalse(facet_type_obj.meervoudig_toegestaan)
