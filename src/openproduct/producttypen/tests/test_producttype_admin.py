from django.test import TestCase

from ..admin.producttype import ProductTypeAdminForm
from ..models import Thema
from .factories import ThemaFactory, UniformeProductNaamFactory


class TestProductTypeAdminForm(TestCase):
    def setUp(self):
        upn = UniformeProductNaamFactory.create()
        self.data = {
            "naam": "test",
            "code": "TEST-123",
            "uniforme_product_naam": upn,
            "beschrijving": "beschrijving",
            "samenvatting": "samenvatting",
            "interne_opmerkingen": "interne opmerkingen",
        }

    def test_at_least_one_thema_is_required(self):
        form = ProductTypeAdminForm(data=self.data)

        self.assertEqual(form.errors, {"themas": ["Er is minimaal één thema vereist."]})

        ThemaFactory.create()
        form = ProductTypeAdminForm(data=self.data | {"themas": Thema.objects.all()})

        self.assertEqual(form.errors, {})
