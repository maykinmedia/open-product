from django.forms import inlineformset_factory
from django.test import TestCase
from django.utils.translation import gettext as _

from openproduct.accounts.tests.factories import UserFactory

from ..admin.subtype import SubTypeInlineFormSet
from ..models import ProductType, SubType
from .factories import ProductTypeFactory

SubTypeFormSet = inlineformset_factory(
    ProductType,
    SubType,
    formset=SubTypeInlineFormSet,
    fields=("naam",),
    extra=0,
)


class TestSubTypeInlineFormSet(TestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory.create(superuser=True)
        self.producttype = ProductTypeFactory.create()

    def _formset(self, forms: list[dict[str, str]]):
        data = {
            "subtypen-TOTAL_FORMS": str(len(forms)),
            "subtypen-INITIAL_FORMS": "0",
            "subtypen-MIN_NUM_FORMS": "0",
            "subtypen-MAX_NUM_FORMS": "1000",
        }
        for idx, form in enumerate(forms):
            data |= {f"subtypen-{idx}-{key}": value for key, value in form.items()}

        return SubTypeFormSet(
            data,
            instance=self.producttype,
            prefix="subtypen",
            _django_user=self.user,
        )

    def test_subtypen(self):
        formset = self._formset([{"naam": "spoed"}, {"naam": "regulier"}])

        self.assertTrue(formset.is_valid(), formset.errors)
        formset.save()

        self.assertEqual(self.producttype.subtypen.count(), 2)

    def test_subtypen_with_duplicate_naam(self):
        formset = self._formset([{"naam": "spoed"}, {"naam": "Spoed"}])

        self.assertFalse(formset.is_valid())
        self.assertEqual(
            formset.non_form_errors(),
            [_("Dubbele naam: {} op index {}.").format("Spoed", 1)],
        )
