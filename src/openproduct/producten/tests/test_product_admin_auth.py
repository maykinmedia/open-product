from django.contrib.auth.models import Permission
from django.urls import reverse

from django_webtest import WebTest
from maykin_2fa.test import disable_admin_mfa

from openproduct.accounts.tests.factories import UserFactory
from openproduct.producten.models import Product
from openproduct.producten.tests.factories import ProductFactory
from openproduct.producttypen.models.producttypepermission import PermissionModes
from openproduct.producttypen.tests.factories import (
    ProductTypeFactory,
    ProductTypePermissionFactory,
)


@disable_admin_mfa()
class TestProductAdminAuth(WebTest):
    def setUp(self):
        super().setUp()
        self.user = UserFactory(is_staff=True)
        self.user.user_permissions.set(
            (
                Permission.objects.get(codename="view_product"),
                Permission.objects.get(codename="add_eigenaar"),
                Permission.objects.get(codename="add_product"),
                Permission.objects.get(codename="change_product"),
                Permission.objects.get(codename="delete_product"),
            )
        )
        self.app.set_user(self.user)

    def _fill_form(self, form, producttype, **kwargs):
        form.fields["producttype"][0].options = [
            (str(producttype.pk), False, str(producttype))
        ]  # autocomplete_field is not filled on page load

        form["producttype"] = str(producttype.pk)
        form["aanvraag_zaak_url"] = (
            "https://maykin.zaken.nl/4285817c-374f-430e-b199-0209251ac641"
        )
        form["eigenaren-0-bsn"] = "111222333"

        for k in kwargs:
            form[k] = kwargs[k]

    def test_read_product(self):
        product = ProductFactory.create()

        product_url = reverse("admin:producten_product_change", args=[product.id])

        with self.subTest("no permission"):
            response = self.app.get(product_url)
            self.assertEqual(response.status_code, 302)

        ProductTypePermissionFactory.create(
            producttype=ProductTypeFactory.create(),
            user=self.user,
            mode=PermissionModes.read_only,
        )
        with self.subTest("other producttype permission"):
            response = self.app.get(product_url)
            self.assertEqual(response.status_code, 302)

        permission = ProductTypePermissionFactory.create(
            producttype=product.producttype,
            user=self.user,
            mode=PermissionModes.read_only,
        )
        with self.subTest("read permission"):
            response = self.app.get(product_url)
            self.assertEqual(response.status_code, 200)

        permission.mode = PermissionModes.read_and_write
        permission.save()
        with self.subTest("producttype write permission"):
            response = self.app.get(product_url)
            self.assertEqual(response.status_code, 200)

    def test_list_product(self):
        product1 = ProductFactory.create(naam="parkeervergunning abc")
        product2 = ProductFactory.create(naam="id kaart def")

        producten_url = reverse("admin:producten_product_changelist")

        with self.subTest("no permissions"):
            response = self.app.get(producten_url)
            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, "parkeervergunning abc")
            self.assertNotContains(response, "id kaart def")

        ProductTypePermissionFactory.create(
            producttype=product1.producttype,
            user=self.user,
            mode=PermissionModes.read_only,
        )

        ProductTypePermissionFactory.create(
            producttype=product2.producttype,
            user=self.user,
            mode=PermissionModes.read_and_write,
        )

        with self.subTest("with permissions"):
            response = self.app.get(producten_url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "parkeervergunning abc")
            self.assertContains(response, "id kaart def")

    def test_create_product(self):
        producttype = ProductTypeFactory.create(naam="parkeervergunning")

        product_url = reverse("admin:producten_product_add")

        with self.subTest("no permission"):
            response = self.app.get(product_url, expect_errors=True)
            self.assertEqual(response.status_code, 403)

        permission = ProductTypePermissionFactory.create(
            producttype=producttype,
            user=self.user,
            mode=PermissionModes.read_only,
        )
        with self.subTest("read permission"):
            response = self.app.get(product_url, expect_errors=True)
            self.assertEqual(response.status_code, 403)

        permission.mode = PermissionModes.read_and_write
        permission.save()
        with self.subTest("producttype write permission"):
            response = self.app.get(product_url)
            self.assertEqual(response.status_code, 200)

            form = response.forms["product_form"]
            self._fill_form(form, producttype)

            response = form.submit()
            self.assertEqual(response.status_code, 302)
            self.assertEqual(Product.objects.count(), 1)

    def test_update_product(self):
        product = ProductFactory.create()

        product_url = reverse("admin:producten_product_change", args=[product.id])

        with self.subTest("no permission"):
            response = self.app.get(product_url)
            self.assertEqual(response.status_code, 302)

        permission = ProductTypePermissionFactory.create(
            producttype=product.producttype,
            user=self.user,
            mode=PermissionModes.read_only,
        )
        with self.subTest("read permission"):
            response = self.app.get(product_url)
            self.assertEqual(response.status_code, 200)

            form = response.forms["product_form"]
            self.assertNotIn("producttype", form.fields)  # form disabled

        permission.mode = PermissionModes.read_and_write
        permission.save()
        with self.subTest("producttype write permission"):
            response = self.app.get(product_url)
            self.assertEqual(response.status_code, 200)

            form = response.forms["product_form"]
            self._fill_form(form, product.producttype, naam="blabla")

            response = form.submit()
            self.assertEqual(response.status_code, 302)
            self.assertEqual(Product.objects.get().naam, "blabla")

    def test_delete_product(self):
        product = ProductFactory.create()

        product_url = reverse("admin:producten_product_delete", args=[product.id])

        with self.subTest("no permission"):
            response = self.app.get(product_url)
            self.assertEqual(response.status_code, 302)

        permission = ProductTypePermissionFactory.create(
            producttype=product.producttype,
            user=self.user,
            mode=PermissionModes.read_only,
        )
        with self.subTest("read permission"):
            response = self.app.get(product_url, expect_errors=True)
            self.assertEqual(response.status_code, 403)

        permission.mode = PermissionModes.read_and_write
        permission.save()
        with self.subTest("producttype write permission"):
            response = self.app.get(product_url)
            self.assertEqual(response.status_code, 200)
