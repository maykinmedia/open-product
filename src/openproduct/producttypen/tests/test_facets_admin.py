from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext as _

from openproduct.accounts.tests.factories import UserFactory

from ..models import FacetType, FacetWaarde
from .factories import FacetTypeFactory, FacetWaardeFactory


class TestFacetTypeAdmin(TestCase):
    add_url = reverse("admin:producttypen_facettype_add")
    changelist_url = reverse("admin:producttypen_facettype_changelist")

    def setUp(self):
        self.user = UserFactory.create(superuser=True)
        self.client.force_login(self.user)

        self.data = {
            "naam": "doelgroep",
            "omschrijving": "",
            "waarden-TOTAL_FORMS": "0",
            "waarden-INITIAL_FORMS": "0",
            "waarden-MIN_NUM_FORMS": "0",
            "waarden-MAX_NUM_FORMS": "1000",
        }

    def _change_url(self, instance):
        return reverse("admin:producttypen_facettype_change", args=[instance.pk])

    def test_changelist_loads(self):
        FacetTypeFactory.create(naam="doelgroep")

        response = self.client.get(self.changelist_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "doelgroep")

    def test_create_facettype_without_waarden(self):
        response = self.client.post(self.add_url, self.data)

        self.assertEqual(response.status_code, 302)
        facet_type = FacetType.objects.get()
        self.assertEqual(facet_type.naam, "doelgroep")
        self.assertFalse(facet_type.facetteerbaar)
        self.assertFalse(facet_type.meervoudig_toegestaan)
        self.assertFalse(facet_type.verplicht)
        self.assertEqual(facet_type.waarden.count(), 0)

    def test_create_facettype_with_booleans(self):
        data = self.data | {
            "facetteerbaar": "on",
            "meervoudig_toegestaan": "on",
            "verplicht": "on",
        }

        response = self.client.post(self.add_url, data)

        self.assertEqual(response.status_code, 302)
        facet_type = FacetType.objects.get()
        self.assertTrue(facet_type.facetteerbaar)
        self.assertTrue(facet_type.meervoudig_toegestaan)
        self.assertTrue(facet_type.verplicht)

    def test_create_facettype_with_waarden(self):
        data = self.data | {
            "waarden-TOTAL_FORMS": "2",
            "waarden-0-naam": "inwoners",
            "waarden-0-actief": "on",
            "waarden-1-naam": "bedrijven",
        }

        response = self.client.post(self.add_url, data)

        self.assertEqual(response.status_code, 302)
        facet_type = FacetType.objects.get()
        self.assertEqual(
            list(facet_type.waarden.values_list("naam", "actief")),
            [("bedrijven", False), ("inwoners", True)],
        )

    def test_create_facettype_without_naam(self):
        data = self.data | {"naam": ""}

        response = self.client.post(self.add_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["adminform"].form.errors,
            {"naam": [_("This field is required.")]},
        )
        self.assertFalse(FacetType.objects.exists())

    def test_create_waarde_without_naam(self):
        data = self.data | {
            "waarden-TOTAL_FORMS": "1",
            "waarden-0-omschrijving": "zonder naam",
        }

        response = self.client.post(self.add_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["inline_admin_formsets"][0].formset.errors,
            [{"naam": [_("This field is required.")]}],
        )
        self.assertFalse(FacetType.objects.exists())

    # Change

    def test_add_waarde_to_existing_facettype(self):
        facet_type = FacetTypeFactory.create(naam="doelgroep")
        data = self.data | {
            "waarden-TOTAL_FORMS": "1",
            "waarden-0-naam": "inwoners",
            "waarden-0-actief": "on",
        }

        url = reverse("admin:producttypen_facettype_change", args=[facet_type.pk])
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(facet_type.waarden.get().naam, "inwoners")

    def test_update_existing_waarde(self):
        facet_type = FacetTypeFactory.create(naam="doelgroep")
        waarde = FacetWaardeFactory.create(
            facet_type=facet_type, naam="inwoners", actief=True
        )
        data = self.data | {
            "waarden-TOTAL_FORMS": "1",
            "waarden-INITIAL_FORMS": "1",
            "waarden-0-id": str(waarde.pk),
            "waarden-0-facet_type": str(facet_type.pk),
            "waarden-0-naam": "burgers",
            # actief omitted -> False
        }

        url = reverse("admin:producttypen_facettype_change", args=[facet_type.pk])
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        waarde.refresh_from_db()
        self.assertEqual(waarde.naam, "burgers")
        self.assertFalse(waarde.actief)

    def test_delete_waarde_via_inline(self):
        facet_type = FacetTypeFactory.create(naam="doelgroep")
        waarde = FacetWaardeFactory.create(facet_type=facet_type, naam="inwoners")
        data = self.data | {
            "waarden-TOTAL_FORMS": "1",
            "waarden-INITIAL_FORMS": "1",
            "waarden-0-id": str(waarde.pk),
            "waarden-0-facet_type": str(facet_type.pk),
            "waarden-0-naam": "inwoners",
            "waarden-0-DELETE": "on",
        }

        url = reverse("admin:producttypen_facettype_change", args=[facet_type.pk])
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(FacetWaarde.objects.exists())
