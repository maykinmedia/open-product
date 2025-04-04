from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from openproduct.producttypen.admin import ThemaAdmin
from openproduct.producttypen.models import Thema
from openproduct.producttypen.tests.factories import ProductTypeFactory, ThemaFactory


class TestThemaAdmin(TestCase):

    def setUp(self):
        self.admin = ThemaAdmin(Thema, AdminSite())

    def test_get_deleted_objects_when_linked_product_type_has_one_thema(self):
        product_type = ProductTypeFactory(naam="product type")
        product_type.themas.add(ThemaFactory(naam="thema"))
        product_type.save()

        _, _, _, protected = self.admin.get_deleted_objects(
            Thema.objects.all(), self.client.request()
        )
        self.assertEqual(
            protected,
            [
                f"Product Type <a href='/admin/producttypen/producttype/{product_type.id}/change/'>"
                f"product type</a> moet aan een minimaal één thema zijn gelinkt. "
                f"Huidige thema's: thema."
            ],
        )

    def test_get_deleted_objects_when_linked_product_type_has_other_themas(self):
        thema = ThemaFactory()
        product_type = ProductTypeFactory()
        product_type.themas.add(thema)
        product_type.themas.add(ThemaFactory())
        product_type.save()

        _, _, _, protected = self.admin.get_deleted_objects(
            Thema.objects.filter(id=thema.id), self.client.request()
        )
        self.assertEqual(protected, [])

    def test_get_deleted_objects_with_multiple_themas(self):
        product_type = ProductTypeFactory(naam="product type")
        product_type.themas.add(ThemaFactory(naam="thema"))
        product_type.themas.add(ThemaFactory(naam="thema 2"))
        product_type.save()

        _, _, _, protected = self.admin.get_deleted_objects(
            Thema.objects.all(), self.client.request()
        )
        self.assertEqual(
            protected,
            [
                f"Product Type <a href='/admin/producttypen/producttype/{product_type.id}/change/'>"
                f"product type</a> moet aan een minimaal één thema zijn gelinkt. "
                f"Huidige thema's: thema, thema 2."
            ],
        )

    def test_deleting_thema_with_sub_themas_raises_error(self):
        thema = ThemaFactory()
        sub_thema = ThemaFactory(hoofd_thema=thema)

        _, _, _, protected = self.admin.get_deleted_objects(
            Thema.objects.filter(id=thema.id), self.client.request()
        )
        self.assertEqual(protected, [f"Thema: {sub_thema.naam}"])
