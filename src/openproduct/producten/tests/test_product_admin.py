import datetime
from unittest.mock import patch

from django.contrib.auth.models import Permission
from django.test import TestCase, tag
from django.urls import reverse

from maykin_2fa.test import disable_admin_mfa
from playwright.sync_api import expect

from openproduct.accounts.tests.factories import UserFactory
from openproduct.producttypen.models.enums import ProductStateChoices
from openproduct.producttypen.models.producttypepermission import PermissionModes
from openproduct.producttypen.tests.factories import (
    JsonSchemaFactory,
    ProductTypeFactory,
    ProductTypePermissionFactory,
    SubTypeFactory,
)
from openproduct.utils.tests.e2e import DEFAULT_PASSWORD, E2ETestCase

from ..admin.product import ProductAdminForm, get_status_choices
from ..models import Product
from .factories import ProductFactory


class TestProductAdminForm(TestCase):
    def setUp(self):
        self.data = {"status"}

    def test_status_and_dates_are_not_validated_when_not_changed(self):
        data = {
            "producttype": ProductTypeFactory.create(toegestane_statussen=[]),
            "status": "gereed",
            "start_datum": datetime.date(2025, 12, 31),
            "eind_datum": datetime.date(2026, 12, 31),
        }

        product = ProductFactory.create(**data)
        data["producttype"] = data.pop("producttype").id
        form = ProductAdminForm(data=data, instance=product)

        form.full_clean()

    @patch("openproduct.producten.admin.product.validate_product_status")
    @patch("openproduct.producten.admin.product.validate_product_start_datum")
    @patch("openproduct.producten.admin.product.validate_product_eind_datum")
    def test_status_and_dates_are_validated_when_changed(
        self,
        mock_validate_product_status,
        mock_validate_product_start_datum,
        mock_validate_product_eind_datum,
    ):
        data = {
            "producttype": ProductTypeFactory.create(toegestane_statussen=["gereed"]),
            "status": "initeel",
            "start_datum": datetime.date(2025, 12, 31),
            "eind_datum": datetime.date(2026, 12, 31),
            "prijs": "10",
            "aanvraag_zaak_urn": "urn:nld:maykin:openzaak:ztc:zaak:uuid:d42613cd-ee22-4455-808c-c19c7b8442a1",
            "frequentie": "eenmalig",
        }

        product = ProductFactory.create(**data)
        data["producttype"] = data.pop("producttype").id
        data["status"] = "gereed"
        data["start_datum"] = datetime.date(2025, 11, 30)
        data["eind_datum"] = datetime.date(2026, 11, 30)
        form = ProductAdminForm(data=data, instance=product)

        form.full_clean()
        mock_validate_product_status.assert_called_once()
        mock_validate_product_start_datum.assert_called_once()
        mock_validate_product_eind_datum.assert_called_once()

    @patch("openproduct.producten.admin.product.validate_product_status")
    @patch("openproduct.producten.admin.product.validate_product_start_datum")
    @patch("openproduct.producten.admin.product.validate_product_eind_datum")
    def test_status__and_dates_are_validated_when_producttype_is_changed(
        self,
        mock_validate_product_status,
        mock_validate_product_start_datum,
        mock_validate_product_eind_datum,
    ):
        data = {
            "producttype": ProductTypeFactory.create(toegestane_statussen=["gereed"]),
            "status": "gereed",
            "start_datum": datetime.date(2025, 12, 31),
            "eind_datum": datetime.date(2026, 12, 31),
            "prijs": "10",
            "aanvraag_zaak_urn": "urn:nld:maykin:openzaak:ztc:zaak:uuid:d42613cd-ee22-4455-808c-c19c7b8442a1",
            "frequentie": "eenmalig",
        }

        product = ProductFactory.create(**data)
        data["producttype"] = ProductTypeFactory.create(toegestane_statussen=[]).id
        form = ProductAdminForm(data=data, instance=product)

        form.full_clean()
        mock_validate_product_status.assert_called_once()
        mock_validate_product_start_datum.assert_called_once()
        mock_validate_product_eind_datum.assert_called_once()

    def test_get_status_choices_with_instance(self):
        producttype = ProductTypeFactory.create(toegestane_statussen=["actief"])
        product = ProductFactory(producttype=producttype, status="gereed")
        choices = get_status_choices(None, product)

        self.assertCountEqual(
            choices,
            [("actief", "Actief"), ("initieel", "Initieel"), ("gereed", "Gereed")],
        )

    def test_get_status_choices_with_producttype_id(self):
        producttype = ProductTypeFactory.create(toegestane_statussen=["actief"])
        choices = get_status_choices(producttype.id, None)

        self.assertCountEqual(choices, [("actief", "Actief"), ("initieel", "Initieel")])

    def test_get_status_choices_with_on_create(self):
        choices = get_status_choices(None, None)

        self.assertEqual(choices, ProductStateChoices.choices)

    def test_valid_verbruiksobject(self):
        data = {
            "producttype": ProductTypeFactory.create(
                verbruiksobject_schema=JsonSchemaFactory(
                    schema={
                        "type": "object",
                        "properties": {"naam": {"type": "string"}},
                        "required": ["naam"],
                    }
                )
            ),
            "status": "initieel",
            "prijs": "10",
            "frequentie": "eenmalig",
            "aanvraag_zaak_urn": "urn:nld:maykin:openzaak:ztc:zaak:uuid:d42613cd-ee22-4455-808c-c19c7b8442a1",
            "verbruiksobject": {"naam": "test"},
        }

        product = ProductFactory.create(**data)
        data["producttype"] = data.pop("producttype").id
        form = ProductAdminForm(data=data, instance=product)
        form.full_clean()
        self.assertEqual(form.errors, {})

    def test_invalid_verbruiksobject(self):
        data = {
            "producttype": ProductTypeFactory.create(
                verbruiksobject_schema=JsonSchemaFactory(
                    schema={
                        "type": "object",
                        "properties": {"naam": {"type": "string"}},
                        "required": ["naam"],
                    }
                )
            ),
            "aanvraag_zaak_urn": "urn:nld:maykin:openzaak:ztc:zaak:uuid:d42613cd-ee22-4455-808c-c19c7b8442a1",
            "status": "initieel",
            "prijs": "10",
            "frequentie": "eenmalig",
            "verbruiksobject": {"test": "test"},
        }

        product = ProductFactory.create(**data)
        data["producttype"] = data.pop("producttype").id
        form = ProductAdminForm(data=data, instance=product)
        form.full_clean()
        self.assertEqual(
            form.errors,
            {"verbruiksobject": ["'naam' is a required property"]},
        )

    def test_verbruiksobject_without_schema(self):
        data = {
            "producttype": ProductTypeFactory.create(),
            "status": "initieel",
            "prijs": "10",
            "frequentie": "eenmalig",
            "verbruiksobject": {"naam": "test"},
            "aanvraag_zaak_urn": "urn:nld:maykin:openzaak:ztc:zaak:uuid:d42613cd-ee22-4455-808c-c19c7b8442a1",
        }

        product = ProductFactory.create(**data)
        data["producttype"] = data.pop("producttype").id
        form = ProductAdminForm(data=data, instance=product)
        form.full_clean()
        self.assertEqual(form.errors, {})

    def test_verbruiksobject_with_schema_without_object(self):
        data = {
            "producttype": ProductTypeFactory.create(
                verbruiksobject_schema=JsonSchemaFactory(
                    schema={
                        "type": "object",
                        "properties": {"naam": {"type": "string"}},
                        "required": ["naam"],
                    }
                )
            ),
            "aanvraag_zaak_urn": "urn:nld:maykin:openzaak:ztc:zaak:uuid:d42613cd-ee22-4455-808c-c19c7b8442a1",
            "status": "initieel",
            "prijs": "10",
            "frequentie": "eenmalig",
        }
        product = ProductFactory.create(**data)
        data["producttype"] = data.pop("producttype").id
        form = ProductAdminForm(data=data, instance=product)
        form.full_clean()
        self.assertEqual(form.errors, {})

    def test_valid_dataobject(self):
        data = {
            "producttype": ProductTypeFactory.create(
                dataobject_schema=JsonSchemaFactory(
                    schema={
                        "type": "object",
                        "properties": {"naam": {"type": "string"}},
                        "required": ["naam"],
                    }
                )
            ),
            "aanvraag_zaak_urn": "urn:nld:maykin:openzaak:ztc:zaak:uuid:d42613cd-ee22-4455-808c-c19c7b8442a1",
            "status": "initieel",
            "prijs": "10",
            "frequentie": "eenmalig",
            "dataobject": {"naam": "test"},
        }

        product = ProductFactory.create(**data)
        data["producttype"] = data.pop("producttype").id
        form = ProductAdminForm(data=data, instance=product)
        form.full_clean()
        self.assertEqual(form.errors, {})

    def test_invalid_dataobject(self):
        data = {
            "producttype": ProductTypeFactory.create(
                dataobject_schema=JsonSchemaFactory(
                    schema={
                        "type": "object",
                        "properties": {"naam": {"type": "string"}},
                        "required": ["naam"],
                    }
                )
            ),
            "aanvraag_zaak_urn": "urn:nld:maykin:openzaak:ztc:zaak:uuid:d42613cd-ee22-4455-808c-c19c7b8442a1",
            "status": "initieel",
            "prijs": "10",
            "frequentie": "eenmalig",
            "dataobject": {"test": "test"},
        }

        product = ProductFactory.create(**data)
        data["producttype"] = data.pop("producttype").id
        form = ProductAdminForm(data=data, instance=product)
        form.full_clean()
        self.assertEqual(
            form.errors,
            {"dataobject": ["'naam' is a required property"]},
        )

    def test_dataobject_without_schema(self):
        data = {
            "producttype": ProductTypeFactory.create(),
            "status": "initieel",
            "prijs": "10",
            "frequentie": "eenmalig",
            "aanvraag_zaak_urn": "urn:nld:maykin:openzaak:ztc:zaak:uuid:d42613cd-ee22-4455-808c-c19c7b8442a1",
            "dataobject": {"naam": "test"},
        }

        product = ProductFactory.create(**data)
        data["producttype"] = data.pop("producttype").id
        form = ProductAdminForm(data=data, instance=product)
        form.full_clean()
        self.assertEqual(form.errors, {})

    def test_dataobject_with_schema_without_object(self):
        data = {
            "producttype": ProductTypeFactory.create(
                dataobject_schema=JsonSchemaFactory(
                    schema={
                        "type": "object",
                        "properties": {"naam": {"type": "string"}},
                        "required": ["naam"],
                    }
                )
            ),
            "status": "initieel",
            "prijs": "10",
            "aanvraag_zaak_urn": "urn:nld:urn:nld:maykin:openzaak:ztc:zaak:uuid:d42613cd-ee22-4455-808c-c19c7b8442a1",
            "frequentie": "eenmalig",
        }
        product = ProductFactory.create(**data)
        data["producttype"] = data.pop("producttype").id
        form = ProductAdminForm(data=data, instance=product)
        form.full_clean()
        self.assertEqual(form.errors, {})

    def test_subtype(self):
        producttype = ProductTypeFactory.create()
        other_subtype = SubTypeFactory.create()

        data = {
            "producttype": producttype.id,
            "status": "initieel",
            "aanvraag_zaak_urn": "urn:nld:urn:nld:maykin:openzaak:ztc:zaak:uuid:d42613cd-ee22-4455-808c-c19c7b8442a1",
        }

        with self.subTest("no pt.subtypen no p.subtype"):
            form = ProductAdminForm(data=data)
            form.full_clean()
            self.assertEqual(form.errors, {})

        with self.subTest("no pt.subtypen with p.subtype"):
            form = ProductAdminForm(data=data | {"subtype": other_subtype.id})
            form.full_clean()
            self.assertIn("subtype", form.errors)

        subtype = SubTypeFactory.create(producttype=producttype, naam="spoed")

        with self.subTest("with pt.subtypen no p.subtype"):
            form = ProductAdminForm(data=data)
            form.full_clean()
            self.assertEqual(
                form.errors,
                {
                    "subtype": [
                        "Subtype is verplicht als het producttype subtypen heeft."
                    ]
                },
            )

        with self.subTest("with pt.subtypen with correct p.subtype"):
            form = ProductAdminForm(data=data | {"subtype": subtype.id})
            form.full_clean()
            self.assertEqual(form.errors, {})

        with self.subTest("with pt.subtypen with subtype of other producttype"):
            form = ProductAdminForm(data=data | {"subtype": other_subtype.id})
            form.full_clean()
            self.assertIn("subtype", form.errors)

    def test_subtype_on_existing_product(self):
        producttype = ProductTypeFactory.create()
        other_producttype = ProductTypeFactory.create()
        product_without_subtype = ProductFactory.create(producttype=producttype)
        subtype = SubTypeFactory.create(producttype=producttype, naam="spoed")
        other_subtype = SubTypeFactory.create(producttype=other_producttype)
        product_with_subtype = ProductFactory.create(
            producttype=producttype, subtype=subtype
        )

        data = {
            "producttype": producttype.id,
            "status": "initieel",
            "aanvraag_zaak_urn": "urn:nld:urn:nld:maykin:openzaak:ztc:zaak:uuid:d42613cd-ee22-4455-808c-c19c7b8442a1",
        }
        required_error = {
            "subtype": ["Subtype is verplicht als het producttype subtypen heeft."]
        }

        with self.subTest("existing product without subtype"):
            form = ProductAdminForm(data=data, instance=product_without_subtype)
            form.full_clean()
            self.assertEqual(form.errors, {})

        with self.subTest("existing product without subtype changing producttype"):
            form = ProductAdminForm(
                data=data | {"producttype": other_producttype.id},
                instance=product_without_subtype,
            )
            form.full_clean()
            self.assertEqual(form.errors, required_error)

            form = ProductAdminForm(
                data=data
                | {"producttype": other_producttype.id, "subtype": other_subtype.id},
                instance=product_without_subtype,
            )
            form.full_clean()
            self.assertEqual(form.errors, {})

        with self.subTest("clearing subtype"):
            form = ProductAdminForm(data=data, instance=product_with_subtype)
            form.full_clean()
            self.assertEqual(form.errors, required_error)

    def test_subtype_queryset_is_limited_to_producttype(self):
        producttype = ProductTypeFactory.create()
        subtype = SubTypeFactory.create(producttype=producttype)
        SubTypeFactory.create()

        with self.subTest("unbound without producttype"):
            form = ProductAdminForm()
            self.assertQuerySetEqual(form.fields["subtype"].queryset, [])

        with self.subTest("bound"):
            form = ProductAdminForm(data={"producttype": producttype.id})
            self.assertQuerySetEqual(form.fields["subtype"].queryset, [subtype])

        with self.subTest("instance"):
            product = ProductFactory.create(producttype=producttype, subtype=subtype)
            form = ProductAdminForm(instance=product)
            self.assertQuerySetEqual(form.fields["subtype"].queryset, [subtype])


@tag("playwright")
@disable_admin_mfa()
class TestProductSubtypenView(TestCase):
    url = reverse("admin:producten_product_subtypen")

    def setUp(self):
        super().setUp()
        self.producttype = ProductTypeFactory.create()
        self.subtype = SubTypeFactory.create(producttype=self.producttype)
        SubTypeFactory.create()

    def test_subtypen_json(self):
        self.client.force_login(UserFactory.create(superuser=True))
        url = self.url

        with self.subTest("subtypen of producttype"):
            response = self.client.get(url, {"producttype": self.producttype.pk})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json(), [{"id": self.subtype.pk, "name": self.subtype.naam}]
            )

        with self.subTest("no producttype"):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), [])

        with self.subTest("invalid producttype"):
            response = self.client.get(url, {"producttype": "abc"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), [])

        with self.subTest("unknown producttype"):
            response = self.client.get(url, {"producttype": 999999})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), [])

    def test_subtypen_json_permissions(self):
        data = {"producttype": self.producttype.pk}

        with self.subTest("requires login"):
            response = self.client.get(self.url, data)
            self.assertEqual(response.status_code, 302)
            self.assertIn(reverse("admin:login"), response["Location"])

        with self.subTest("requires is_staff"):
            self.client.force_login(UserFactory.create(is_staff=False))
            response = self.client.get(self.url, data)
            self.assertEqual(response.status_code, 302)

        user = UserFactory.create(is_staff=True)
        self.client.force_login(user)

        with self.subTest("requires view permission"):
            response = self.client.get(self.url, data)
            self.assertEqual(response.status_code, 403)

        user.user_permissions.add(Permission.objects.get(codename="view_product"))

        with self.subTest("no producttype permission"):
            response = self.client.get(self.url, data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), [])

        ProductTypePermissionFactory.create(
            producttype=ProductTypeFactory.create(),
            user=user,
            mode=PermissionModes.read_only,
        )

        with self.subTest("other producttype permission"):
            response = self.client.get(self.url, data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), [])

        ProductTypePermissionFactory.create(
            producttype=self.producttype,
            user=user,
            mode=PermissionModes.read_only,
        )

        with self.subTest("producttype read permission"):
            response = self.client.get(self.url, data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json(), [{"id": self.subtype.pk, "name": self.subtype.naam}]
            )


@disable_admin_mfa()
class TestProductSubtypeAdmin(E2ETestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory.create(superuser=True, password=DEFAULT_PASSWORD)
        self.add_url = self.live_reverse("admin:producten_product_add")

    def _subtype(self, page):
        return page.locator("#id_subtype")

    def _real_options(self, select):
        return select.locator("option:not([value=''])")

    def _option_values(self, select):
        return self._real_options(select).evaluate_all("opts => opts.map(o => o.value)")

    def _select_producttype(self, page, producttype):
        # producttype is an autocomplete (select2) field
        page.locator(".field-producttype .select2-selection").click()
        page.locator(".select2-search__field").fill(producttype.code)
        page.get_by_role("option", name=producttype.code, exact=True).click()

    def _fill_required(self, page):
        page.locator("#id_aanvraag_zaak_url").fill(
            "https://maykin.zaken.nl/4285817c-374f-430e-b199-0209251ac641"
        )
        page.locator("#id_eigenaren-0-bsn").fill("111222333")

    def _save(self, page):
        page.click("input[name=_save]")

    def test_add_product_with_subtype(self):
        producttype = ProductTypeFactory.create()
        subtype = SubTypeFactory.create(producttype=producttype)
        SubTypeFactory.create(producttype=producttype)
        SubTypeFactory.create()

        page = self.new_page(self.user)
        page.goto(self.add_url)

        subtype_select = self._subtype(page)
        self._select_producttype(page, producttype)

        expected = [str(pk) for pk in producttype.subtypen.values_list("pk", flat=True)]
        expect(self._real_options(subtype_select)).to_have_count(len(expected))
        self.assertCountEqual(self._option_values(subtype_select), expected)

        subtype_select.select_option(str(subtype.pk))
        self._fill_required(page)
        self._save(page)

        expect(page.locator(".messagelist .success")).to_be_visible()
        self.assertEqual(Product.objects.get().subtype, subtype)

    def test_no_producttype_selected_has_no_subtype_options(self):
        SubTypeFactory.create()

        page = self.new_page(self.user)
        page.goto(self.add_url)

        expect(self._real_options(self._subtype(page))).to_have_count(0)

    def test_producttype_without_subtypen_has_no_subtype_options(self):
        producttype = ProductTypeFactory.create()
        SubTypeFactory.create()

        page = self.new_page(self.user)
        page.goto(self.add_url)

        self._select_producttype(page, producttype)
        expect(self._subtype(page)).to_be_enabled()
        expect(self._real_options(self._subtype(page))).to_have_count(0)

    def test_changing_producttype_updates_subtype_options(self):
        producttype_a = ProductTypeFactory.create()
        producttype_b = ProductTypeFactory.create()
        subtype_a = SubTypeFactory.create(producttype=producttype_a)
        SubTypeFactory.create_batch(3, producttype=producttype_b)

        page = self.new_page(self.user)
        page.goto(self.add_url)

        subtype_select = self._subtype(page)

        # first select
        self._select_producttype(page, producttype_a)
        expect(
            subtype_select.locator(f"option[value='{subtype_a.pk}']")
        ).to_be_attached()
        subtype_select.select_option(str(subtype_a.pk))

        # second select
        self._select_producttype(page, producttype_b)

        expect(self._real_options(subtype_select)).to_have_count(3)
        expect(subtype_select.locator(f"option[value='{subtype_a.pk}']")).to_have_count(
            0
        )
        expect(subtype_select).not_to_have_value(str(subtype_a.pk))

    def test_change_page_has_subtypen_of_producttype(self):
        producttype = ProductTypeFactory.create()
        subtype = SubTypeFactory.create(producttype=producttype)
        SubTypeFactory.create(producttype=producttype)
        SubTypeFactory.create()
        product = ProductFactory.create(producttype=producttype, subtype=subtype)

        page = self.new_page(self.user)
        page.goto(
            self.live_reverse("admin:producten_product_change", args=[product.pk])
        )

        subtype_select = self._subtype(page)
        expect(self._real_options(subtype_select)).to_have_count(2)
        expect(subtype_select).to_have_value(str(subtype.pk))

    def test_subtype_required_when_producttype_has_subtypen(self):
        producttype = ProductTypeFactory.create()
        SubTypeFactory.create(producttype=producttype)

        page = self.new_page(self.user)
        page.goto(self.add_url)

        self._select_producttype(page, producttype)
        expect(self._real_options(self._subtype(page))).to_have_count(1)
        self._fill_required(page)
        self._save(page)

        expect(page.locator(".errornote")).to_be_visible()
        expect(page.locator(".field-subtype .errorlist")).to_contain_text(
            "Subtype is verplicht als het producttype subtypen heeft."
        )
        self.assertFalse(Product.objects.exists())
