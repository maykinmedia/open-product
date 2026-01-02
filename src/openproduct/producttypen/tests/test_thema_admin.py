from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from openproduct.producttypen.admin import ThemaAdmin
from openproduct.producttypen.models import ContentElement, Thema
from openproduct.producttypen.tests.factories import ProductTypeFactory, ThemaFactory


class TestThemaAdmin(TestCase):
    def setUp(self):
        self.admin = ThemaAdmin(Thema, AdminSite())

        self.producttype = ProductTypeFactory()

        self.ce1 = ContentElement.objects.create(
            producttype=self.producttype, content="Content Element 1"
        )
        self.ce2 = ContentElement.objects.create(
            producttype=self.producttype, content="Content Element 2"
        )

        self.thema = ThemaFactory()
        self.sub_thema = ThemaFactory(hoofd_thema=self.thema)

    def test_get_deleted_objects_when_linked_producttype_has_one_thema(self):
        producttype = ProductTypeFactory(naam="producttype", code="PT")
        producttype.themas.add(ThemaFactory(naam="thema"))
        producttype.save()

        _, _, _, protected = self.admin.get_deleted_objects(
            Thema.objects.all(), self.client.request()
        )
        self.assertEqual(
            protected,
            [
                f"Producttype <a href='/admin/producttypen/producttype/{producttype.id}/change/'>"
                f"PT</a> moet aan een minimaal één thema zijn gelinkt. "
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
        producttype = ProductTypeFactory(naam="producttype", code="PT")
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
                f"PT</a> moet aan een minimaal één thema zijn gelinkt. "
                f"Huidige thema's: thema 2, thema."
            ],
        )

    def test_deleting_thema_with_sub_themas_raises_error(self):
        _, _, _, protected = self.admin.get_deleted_objects(
            Thema.objects.filter(id=self.thema.id), self.client.request()
        )
        self.assertEqual(protected, [f"Thema: {self.sub_thema.naam}"])

    def test_producttypen_count_method(self):
        pt = ProductTypeFactory()
        self.thema.producttypen.add(pt)

        annotated_thema = self.admin.get_queryset(self.client.request()).get(
            pk=self.thema.pk
        )
        self.assertEqual(self.admin.producttypen_count(annotated_thema), 1)

    def test_content_elementen_count_method(self):
        self.thema.content_elementen.set([self.ce1, self.ce2])
        self.assertEqual(self.admin.content_elementen_count(self.thema), 2)

    def test_content_elementen_count_empty(self):
        self.assertEqual(self.admin.content_elementen_count(self.sub_thema), 0)
