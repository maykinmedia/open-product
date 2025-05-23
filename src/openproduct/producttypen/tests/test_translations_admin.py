from django.urls import reverse

from django_webtest import WebTest
from maykin_2fa.test import disable_admin_mfa

from openproduct.accounts.tests.factories import UserFactory
from openproduct.producttypen.models import (
    ContentElementTranslation,
    ProductTypeTranslation,
)
from openproduct.producttypen.tests.factories import (
    ContentElementFactory,
    ProductTypeFactory,
)


@disable_admin_mfa()
class TestTranslationsAdmin(WebTest):
    def setUp(self):
        super().setUp()
        self.user = UserFactory.create(superuser=True)
        self.app.set_user(self.user)

        self.producttype = ProductTypeFactory()
        self.contentelement = ContentElementFactory.create(producttype=self.producttype)

    def test_producttype_translation_cannot_be_deleted_from_admin(self):
        translation = ProductTypeTranslation.objects.get(master=self.producttype)

        translation_url = reverse(
            "admin:producttypen_producttypetranslation_change", args=[translation.id]
        )

        response = self.app.get(translation_url)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Verwijderen", response.text)

    def test_contentelement_translation_cannot_be_deleted_from_admin(self):
        translation = ContentElementTranslation.objects.get(master=self.contentelement)

        translation_url = reverse(
            "admin:producttypen_contentelementtranslation_change", args=[translation.id]
        )

        response = self.app.get(translation_url)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Verwijderen", response.text)

    def test_producttype_add_view_only_has_nl_tab(self):
        url = reverse("admin:producttypen_producttype_add")

        response = self.app.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Nederlands", response.text)
        self.assertNotIn("Engels", response.text)

    def test_producttype_change_view_has_all_tabs(self):
        url = reverse(
            "admin:producttypen_producttype_change", args=[self.producttype.id]
        )

        response = self.app.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Nederlands", response.text)
        self.assertIn("Engels", response.text)

    def test_translations_are_deleted_with_producttype(self):
        self.assertEqual(ProductTypeTranslation.objects.count(), 1)
        self.assertEqual(ContentElementTranslation.objects.count(), 1)

        url = reverse(
            "admin:producttypen_producttype_change", args=[self.producttype.id]
        )

        response = self.app.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Verwijderen", response.text)

        delete_url = reverse(
            "admin:producttypen_producttype_delete", args=[self.producttype.id]
        )
        response = self.app.get(delete_url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Weet u het zeker?", response.text)

        form = response.forms[0]
        form.submit({"post": "yes"})

        self.assertEqual(ProductTypeTranslation.objects.count(), 0)
        self.assertEqual(ContentElementTranslation.objects.count(), 0)
