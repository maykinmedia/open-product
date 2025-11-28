from django.db.migrations.exceptions import IrreversibleError
from django.test import override_settings

from openproduct.producten.models import Document, Taak, Zaak
from openproduct.producten.tests.factories import ProductFactory
from openproduct.urn.models import UrnMappingConfig
from openproduct.utils.tests.cases import BaseMigrationTest


class TestExterneVerwijzingRemovalMigrations(BaseMigrationTest):
    app = "producten"
    migrate_to = "0014_remove_document_uuid_remove_taak_uuid_and_more"
    migrate_from = "0012_alter_product_frequentie_alter_product_prijs"

    def setUp(self):
        super().setUp()

        _ExterneVerwijzingConfig = self.old_app_state.get_model(
            "producttypen", "ExterneVerwijzingConfig"
        )

        _Zaak = self.old_app_state.get_model("producten", "Zaak")
        _Taak = self.old_app_state.get_model("producten", "Taak")
        _Document = self.old_app_state.get_model("producten", "Document")

        _ExterneVerwijzingConfig.objects.create(
            documenten_url="https://documenten.maykin.nl/documenten",
            zaken_url="https://zaken.maykin.nl/zaken",
            taken_url="https://taken.maykin.nl/taken",
        )

        product = ProductFactory.create()

        _Zaak.objects.create(
            uuid="1c8cc827-d537-40cd-9558-b5731e240620", product_id=product.id
        )
        _Taak.objects.create(
            uuid="1c8cc827-d537-40cd-9558-b5731e240621", product_id=product.id
        )
        _Document.objects.create(
            uuid="1c8cc827-d537-40cd-9558-b5731e240622", product_id=product.id
        )

    @override_settings(REQUIRE_URL_URN_MAPPING=True)
    def test_without_required_urn_mapping(self):
        with self.assertRaises(IrreversibleError):
            self._perform_migration()

    @override_settings(REQUIRE_URL_URN_MAPPING=False)
    def test_without_urn_mapping(self):
        self._perform_migration()

        self.assertEqual(
            Zaak.objects.get().url,
            "https://zaken.maykin.nl/zaken/1c8cc827-d537-40cd-9558-b5731e240620",
        )
        self.assertEqual(
            Taak.objects.get().url,
            "https://taken.maykin.nl/taken/1c8cc827-d537-40cd-9558-b5731e240621",
        )
        self.assertEqual(
            Document.objects.get().url,
            "https://documenten.maykin.nl/documenten/1c8cc827-d537-40cd-9558-b5731e240622",
        )

        self.assertIsNone(Zaak.objects.get().urn)
        self.assertIsNone(Taak.objects.get().urn)
        self.assertIsNone(Document.objects.get().urn)

    def test_with_urn_mapping(self):
        UrnMappingConfig.objects.create(
            url="https://documenten.maykin.nl/documenten", urn="maykin:abc:drc:document"
        )
        UrnMappingConfig.objects.create(
            url="https://taken.maykin.nl/taken", urn="maykin:abc:trc:taak"
        )
        UrnMappingConfig.objects.create(
            url="https://zaken.maykin.nl/zaken", urn="maykin:abc:zrc:zaak"
        )

        self._perform_migration()

        self.assertEqual(
            Zaak.objects.get().url,
            "https://zaken.maykin.nl/zaken/1c8cc827-d537-40cd-9558-b5731e240620",
        )
        self.assertEqual(
            Taak.objects.get().url,
            "https://taken.maykin.nl/taken/1c8cc827-d537-40cd-9558-b5731e240621",
        )
        self.assertEqual(
            Document.objects.get().url,
            "https://documenten.maykin.nl/documenten/1c8cc827-d537-40cd-9558-b5731e240622",
        )

        self.assertEqual(
            Zaak.objects.get().urn,
            "maykin:abc:zrc:zaak:1c8cc827-d537-40cd-9558-b5731e240620",
        )
        self.assertEqual(
            Taak.objects.get().urn,
            "maykin:abc:trc:taak:1c8cc827-d537-40cd-9558-b5731e240621",
        )
        self.assertEqual(
            Document.objects.get().urn,
            "maykin:abc:drc:document:1c8cc827-d537-40cd-9558-b5731e240622",
        )
