from django.contrib.auth.models import Permission
from django.test import override_settings
from django.urls import reverse, reverse_lazy

from rest_framework import status

from openproduct.accounts.models import User
from openproduct.producten.tests.factories import ProductFactory
from openproduct.producttypen.models.producttypepermission import PermissionModes
from openproduct.producttypen.tests.factories import (
    ProductTypeFactory,
    ProductTypePermissionFactory,
)
from openproduct.urn.models import UrnMappingConfig
from openproduct.utils.tests.cases import BaseApiTestCase


@override_settings(NOTIFICATIONS_DISABLED=True, PRODUCTEN_API_MAJOR_VERSION=0)
class TestProductAuth(BaseApiTestCase):
    path = reverse_lazy("product-list")

    def setUp(self):
        super().setUp()
        self.user = User.objects.get()

        self.producttype = ProductTypeFactory.create()
        self.data = {
            "producttype_uuid": self.producttype.uuid,
            "status": "initieel",
            "prijs": "20.20",
            "frequentie": "eenmalig",
            "eigenaren": [{"kvk_nummer": "12345678"}],
            "aanvraag_zaak_urn": "maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
        }

        UrnMappingConfig.objects.create(
            urn="maykin:abc:ztc:zaak",
            url="https://maykin.ztc.com/api/v1/zaken",
        )

    def detail_path(self, product):
        return reverse("product-detail", args=[product.uuid])

    def assertStatusCode(self, method, expected_code, instance=None, data=None):
        path = self.detail_path(instance) if instance else self.path
        response = getattr(self.client, method)(path, data)
        self.assertEqual(response.status_code, expected_code, response.data)
        return response

    def test_read_product(self):
        product = ProductFactory.create()

        with self.subTest("no permissions"):
            self.assertStatusCode("get", status.HTTP_403_FORBIDDEN, product)

        self.user.user_permissions.add(Permission.objects.get(codename="view_product"))

        with self.subTest("class permission"):
            self.assertStatusCode("get", status.HTTP_403_FORBIDDEN, product)

        permission = ProductTypePermissionFactory.create(
            producttype=product.producttype,
            user=self.user,
            mode=PermissionModes.read_only,
        )

        with self.subTest("producttype read permission"):
            self.assertStatusCode("get", status.HTTP_200_OK, product)

        permission.mode = PermissionModes.read_and_write
        permission.save()
        with self.subTest("producttype write permission"):
            self.assertStatusCode("get", status.HTTP_200_OK, product)

    def test_list_product(self):
        product1 = ProductFactory.create()
        product2 = ProductFactory.create()

        with self.subTest("no permissions"):
            self.assertStatusCode("get", status.HTTP_403_FORBIDDEN)

        self.user.user_permissions.add(Permission.objects.get(codename="view_product"))

        with self.subTest("class permission"):
            response = self.assertStatusCode("get", status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 0)

        permission = ProductTypePermissionFactory.create(
            producttype=product1.producttype,
            user=self.user,
            mode=PermissionModes.read_only,
        )

        with self.subTest("producttype read permission"):
            response = self.assertStatusCode("get", status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

        permission.mode = PermissionModes.read_and_write
        permission.save()
        with self.subTest("producttype write permission"):
            response = self.assertStatusCode("get", status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

        ProductTypePermissionFactory.create(
            producttype=product2.producttype,
            user=self.user,
            mode=PermissionModes.read_only,
        )

        with self.subTest("producttype read permission 2"):
            response = self.assertStatusCode("get", status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 2)

    def test_create_product(self):
        with self.subTest("no permissions"):
            self.assertStatusCode("post", status.HTTP_403_FORBIDDEN, data=self.data)

        self.user.user_permissions.add(Permission.objects.get(codename="add_product"))

        with self.subTest("class permission"):
            self.assertStatusCode("post", status.HTTP_403_FORBIDDEN, data=self.data)

        permission = ProductTypePermissionFactory.create(
            producttype=self.producttype, user=self.user, mode=PermissionModes.read_only
        )

        with self.subTest("producttype read permission"):
            self.assertStatusCode("post", status.HTTP_403_FORBIDDEN, data=self.data)

        permission.mode = PermissionModes.read_and_write
        permission.save()
        with self.subTest("producttype write permission"):
            self.assertStatusCode("post", status.HTTP_201_CREATED, data=self.data)

    def test_update_product(self):
        product = ProductFactory.create(producttype=self.producttype)

        with self.subTest("no permissions"):
            self.assertStatusCode("put", status.HTTP_403_FORBIDDEN, product, self.data)

        self.user.user_permissions.add(
            Permission.objects.get(codename="change_product")
        )

        with self.subTest("class permission"):
            self.assertStatusCode("put", status.HTTP_403_FORBIDDEN, product, self.data)

        permission = ProductTypePermissionFactory.create(
            producttype=self.producttype, user=self.user, mode=PermissionModes.read_only
        )

        with self.subTest("producttype read permission"):
            self.assertStatusCode("put", status.HTTP_403_FORBIDDEN, product, self.data)

        permission.mode = PermissionModes.read_and_write
        permission.save()
        with self.subTest("producttype write permission"):
            self.assertStatusCode("put", status.HTTP_200_OK, product, self.data)

    def test_partial_update_product(self):
        product = ProductFactory.create(
            producttype=self.producttype,
            aanvraag_zaak_urn="maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
        )
        data = {"naam": "test"}

        with self.subTest("no permissions"):
            self.assertStatusCode("patch", status.HTTP_403_FORBIDDEN, product, data)

        self.user.user_permissions.add(
            Permission.objects.get(codename="change_product")
        )

        with self.subTest("class permission"):
            self.assertStatusCode("patch", status.HTTP_403_FORBIDDEN, product, data)

        permission = ProductTypePermissionFactory.create(
            producttype=self.producttype, user=self.user, mode=PermissionModes.read_only
        )

        with self.subTest("producttype read permission"):
            self.assertStatusCode("patch", status.HTTP_403_FORBIDDEN, product, data)

        permission.mode = PermissionModes.read_and_write
        permission.save()
        with self.subTest("producttype write permission"):
            self.assertStatusCode("patch", status.HTTP_200_OK, product, data)

    def test_update_product_change_producttype(self):
        product = ProductFactory.create(
            producttype=self.producttype,
            aanvraag_zaak_urn="maykin:abc:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
        )
        producttype = ProductTypeFactory.create()
        data = {"producttype_uuid": producttype.uuid}

        self.user.user_permissions.add(
            Permission.objects.get(codename="change_product")
        )

        with self.subTest("no object permissions"):
            self.assertStatusCode("patch", status.HTTP_403_FORBIDDEN, product, data)

        with self.subTest("new producttype permission only"):
            ProductTypePermissionFactory.create(
                producttype=producttype,
                user=self.user,
                mode=PermissionModes.read_and_write,
            )

            self.assertStatusCode("patch", status.HTTP_403_FORBIDDEN, product, data)

        with self.subTest("both permissions"):
            ProductTypePermissionFactory.create(
                producttype=self.producttype,
                user=self.user,
                mode=PermissionModes.read_and_write,
            )

            self.assertStatusCode("patch", status.HTTP_200_OK, product, data)

        with self.subTest("existing producttype permission only"):
            producttype = ProductTypeFactory.create()
            data = {"producttype_uuid": producttype.uuid}

            self.assertStatusCode("patch", status.HTTP_403_FORBIDDEN, product, data)

    def test_delete_product(self):
        product = ProductFactory.create()

        with self.subTest("no permissions"):
            self.assertStatusCode("delete", status.HTTP_403_FORBIDDEN, product)

        self.user.user_permissions.add(
            Permission.objects.get(codename="delete_product")
        )

        with self.subTest("class permission"):
            self.assertStatusCode("delete", status.HTTP_403_FORBIDDEN, product)

        permission = ProductTypePermissionFactory.create(
            producttype=product.producttype,
            user=self.user,
            mode=PermissionModes.read_only,
        )

        with self.subTest("producttype read permission"):
            self.assertStatusCode("delete", status.HTTP_403_FORBIDDEN, product)

        permission.mode = PermissionModes.read_and_write
        permission.save()
        with self.subTest("producttype write permission"):
            self.assertStatusCode("delete", status.HTTP_204_NO_CONTENT, product)
