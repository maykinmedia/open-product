from django.contrib.auth.models import Permission
from django.test import override_settings
from django.urls import reverse, reverse_lazy

from guardian.shortcuts import assign_perm
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from openproduct.accounts.tests.factories import UserFactory
from openproduct.producten.tests.factories import ProductFactory


@override_settings(NOTIFICATIONS_DISABLED=True)
class TestProduct(APITestCase):
    path = reverse_lazy("product-list")

    def setUp(self):
        self.product = ProductFactory.create()

        self.detail_path = reverse("product-detail", args=[self.product.uuid])

        self.user = UserFactory()
        self.user.user_permissions.set(
            Permission.objects.filter(codename__contains="_product")
        )

        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

    def test_view_perm(self):
        with self.subTest("without pt.producten & view"):
            response = self.client.get(self.detail_path)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        assign_perm("producten", self.user, self.product.producttype)

        with self.subTest("without view"):
            response = self.client.get(self.detail_path)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        with self.subTest("with"):
            assign_perm("view_product", self.user, self.product)

            response = self.client.get(self.detail_path)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_perm(self):
        with self.subTest("without pt.producten, view & change"):
            response = self.client.patch(self.detail_path, {})
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        assign_perm("producten", self.user, self.product.producttype)

        with self.subTest("without view & change"):
            response = self.client.patch(self.detail_path, {})
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        assign_perm("view_product", self.user, self.product)

        with self.subTest("without change"):
            response = self.client.patch(self.detail_path, {})
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest("with"):
            assign_perm("change_product", self.user, self.product)

            response = self.client.get(self.detail_path, {})
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_perm(self):
        with self.subTest("without pt.producten, view & delete"):
            response = self.client.delete(self.detail_path)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        assign_perm("producten", self.user, self.product.producttype)

        with self.subTest("without view & delete"):
            response = self.client.delete(self.detail_path)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        assign_perm("view_product", self.user, self.product)

        with self.subTest("without delete"):
            response = self.client.delete(self.detail_path)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest("with"):
            assign_perm("delete_product", self.user, self.product)

            response = self.client.delete(self.detail_path)
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
