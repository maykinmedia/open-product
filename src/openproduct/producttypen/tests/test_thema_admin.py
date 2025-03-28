from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from openproduct.producttypen.admin import ThemaAdmin
from openproduct.producttypen.models import Thema
from openproduct.producttypen.tests.factories import ProductTypeFactory, ThemaFactory


class TestThemaAdmin(TestCase):

    def setUp(self):
        self.admin = ThemaAdmin(Thema, AdminSite())

    def test_get_deleted_objects_when_linked_producttype_has_one_thema(self):
        producttype = ProductTypeFactory(naam="producttype")
        producttype.themas.add(ThemaFactory(naam="thema"))
        producttype.save()

        _, _, _, protected = self.admin.get_deleted_objects(
            Thema.objects.all(), self.client.request()
        )
        self.assertEqual(
            protected,
            [
                f"Producttype <a href='/admin/producttypen/producttype/{producttype.id}/change/'>"
                f"producttype</a> moet aan een minimaal één thema zijn gelinkt. "
                f"Huidige thema's: thema."
            ],
        )

    def test_get_deleted_objects_when_linked_producttype_has_other_themas(self):
        thema = ThemaFactory()
        producttype = ProductTypeFactory()
        producttype.themas.add(thema)
        producttype.themas.add(ThemaFactory())
        producttype.save()

        _, _, _, protected = self.admin.get_deleted_objects(
            Thema.objects.filter(id=thema.id), self.client.request()
        )
        self.assertEqual(protected, [])

    def test_get_deleted_objects_with_multiple_themas(self):
        producttype = ProductTypeFactory(naam="producttype")
        producttype.themas.add(ThemaFactory(naam="thema"))
        producttype.themas.add(ThemaFactory(naam="thema 2"))
        producttype.save()

        _, _, _, protected = self.admin.get_deleted_objects(
            Thema.objects.all(), self.client.request()
        )
        self.assertEqual(
            protected,
            [
                f"Producttype <a href='/admin/producttypen/producttype/{producttype.id}/change/'>"
                f"producttype</a> moet aan een minimaal één thema zijn gelinkt. "
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
