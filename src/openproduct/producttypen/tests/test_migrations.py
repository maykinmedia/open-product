from django.db.migrations.exceptions import IrreversibleError
from django.test import override_settings

from openproduct.producttypen.models import Proces, VerzoekType, ZaakType
from openproduct.producttypen.models.enums import DoelgroepChoices
from openproduct.urn.models import UrnMappingConfig
from openproduct.utils.tests.cases import BaseMigrationTest


class TestExterneVerwijzingRemovalMigrations(BaseMigrationTest):
    app = "producttypen"
    migrate_to = "0013_remove_proces_uuid_remove_verzoektype_uuid_and_more"
    migrate_from = "0011_contentelementtranslation_aanvullende_informatie"

    def setUp(self):
        super().setUp()

        _ExterneVerwijzingConfig = self.old_app_state.get_model(
            "producttypen", "ExterneVerwijzingConfig"
        )

        _ZaakType = self.old_app_state.get_model("producttypen", "ZaakType")
        _VerzoekTypen = self.old_app_state.get_model("producttypen", "VerzoekType")
        _Proces = self.old_app_state.get_model("producttypen", "Proces")

        _ExterneVerwijzingConfig.objects.create(
            processen_url="https://processen.maykin.nl/processen",
            zaaktypen_url="https://zaaktypen.maykin.nl/zaaktypen",
            verzoektypen_url="https://verzoektypen.maykin.nl/verzoektypen",
        )

        _UniformeProductNaam = self.old_app_state.get_model(
            "producttypen", "UniformeProductNaam"
        )
        _ProductType = self.old_app_state.get_model("producttypen", "ProductType")

        upn = _UniformeProductNaam.objects.create(
            naam="upn 0",
        )

        producttype = _ProductType.objects.create(
            code="producttype code 0",
            uniforme_product_naam=upn,
            doelgroep=DoelgroepChoices.BURGERS,
        )

        _ZaakType.objects.create(
            uuid="1c8cc827-d537-40cd-9558-b5731e240620", producttype_id=producttype.id
        )
        _VerzoekTypen.objects.create(
            uuid="1c8cc827-d537-40cd-9558-b5731e240621", producttype_id=producttype.id
        )
        _Proces.objects.create(
            uuid="1c8cc827-d537-40cd-9558-b5731e240622", producttype_id=producttype.id
        )

    @override_settings(REQUIRE_URL_URN_MAPPING=True)
    def test_without_required_urn_mapping(self):
        with self.assertRaises(IrreversibleError):
            self._perform_migration()

    @override_settings(REQUIRE_URL_URN_MAPPING=False)
    def test_without_urn_mapping(self):
        self._perform_migration()

        self.assertEqual(
            ZaakType.objects.get().url,
            "https://zaaktypen.maykin.nl/zaaktypen/1c8cc827-d537-40cd-9558-b5731e240620",
        )
        self.assertEqual(
            VerzoekType.objects.get().url,
            "https://verzoektypen.maykin.nl/verzoektypen/1c8cc827-d537-40cd-9558-b5731e240621",
        )
        self.assertEqual(
            Proces.objects.get().url,
            "https://processen.maykin.nl/processen/1c8cc827-d537-40cd-9558-b5731e240622",
        )

        self.assertIsNone(ZaakType.objects.get().urn)
        self.assertIsNone(VerzoekType.objects.get().urn)
        self.assertIsNone(Proces.objects.get().urn)

    def test_with_urn_mapping(self):
        UrnMappingConfig.objects.create(
            url="https://processen.maykin.nl/processen",
            urn="urn:nld:maykin:openzaak:ptc:proces",
        )
        UrnMappingConfig.objects.create(
            url="https://verzoektypen.maykin.nl/verzoektypen",
            urn="urn:nld:maykin:openzaak:vtc:verzoektype",
        )
        UrnMappingConfig.objects.create(
            url="https://zaaktypen.maykin.nl/zaaktypen",
            urn="urn:nld:maykin:openzaak:ztc:zaaktype",
        )

        self._perform_migration()

        self.assertEqual(
            ZaakType.objects.get().url,
            "https://zaaktypen.maykin.nl/zaaktypen/1c8cc827-d537-40cd-9558-b5731e240620",
        )
        self.assertEqual(
            VerzoekType.objects.get().url,
            "https://verzoektypen.maykin.nl/verzoektypen/1c8cc827-d537-40cd-9558-b5731e240621",
        )
        self.assertEqual(
            Proces.objects.get().url,
            "https://processen.maykin.nl/processen/1c8cc827-d537-40cd-9558-b5731e240622",
        )

        self.assertEqual(
            ZaakType.objects.get().urn,
            "urn:nld:maykin:openzaak:ztc:zaaktype:1c8cc827-d537-40cd-9558-b5731e240620",
        )
        self.assertEqual(
            VerzoekType.objects.get().urn,
            "urn:nld:maykin:openzaak:vtc:verzoektype:1c8cc827-d537-40cd-9558-b5731e240621",
        )
        self.assertEqual(
            Proces.objects.get().urn,
            "urn:nld:maykin:openzaak:ptc:proces:1c8cc827-d537-40cd-9558-b5731e240622",
        )


class TestUrnPrefixMigration(BaseMigrationTest):
    app = "producttypen"
    migrate_to = "0019_prefix_urns"
    migrate_from = "0018_actie_direct_url_alter_actie_dmn_config_and_more"

    def setUp(self):
        super().setUp()

        _UrnMappingConfig = self.old_app_state.get_model("urn", "UrnMappingConfig")

        _ZaakType = self.old_app_state.get_model("producttypen", "ZaakType")
        _VerzoekTypen = self.old_app_state.get_model("producttypen", "VerzoekType")
        _Proces = self.old_app_state.get_model("producttypen", "Proces")

        _Zaak = self.old_app_state.get_model("producten", "Zaak")
        _Taak = self.old_app_state.get_model("producten", "Taak")
        _Document = self.old_app_state.get_model("producten", "Document")
        _Product = self.old_app_state.get_model("producten", "Product")

        _UniformeProductNaam = self.old_app_state.get_model(
            "producttypen", "UniformeProductNaam"
        )
        _ProductType = self.old_app_state.get_model("producttypen", "ProductType")

        upn = _UniformeProductNaam.objects.create(
            naam="upn 0",
        )

        self.urnmappingconfig = _UrnMappingConfig.objects.create(
            url="https://openzaak.maykin.nl/zaken",
            urn="maykin:openzaak:zrc:zaak",
        )

        producttype = _ProductType.objects.create(
            code="producttype code 0",
            uniforme_product_naam=upn,
            doelgroep=DoelgroepChoices.BURGERS,
        )

        self.zaaktype = _ZaakType.objects.create(
            urn="maykin:openzaak:ztc:zaaktype:1c8cc827-d537-40cd-9558-b5731e240620",
            producttype=producttype,
        )

        self.correct_zaaktype = _ZaakType.objects.create(
            urn="urn:nld:maykin:openzaak:ztc:zaaktype:uuid:1c8cc827-d537-40cd-9558-b5731e240621",
            producttype=producttype,
        )

        self.verzoektype = _VerzoekTypen.objects.create(
            urn="maykin:openzaak:vtc:verzoektype:1c8cc827-d537-40cd-9558-b5731e240621",
            producttype=producttype,
        )
        self.proces = _Proces.objects.create(
            urn="maykin:openzaak:prc:proces:1c8cc827-d537-40cd-9558-b5731e240622",
            producttype=producttype,
        )

        self.product = _Product.objects.create(
            aanvraag_zaak_urn="maykin:openzaak:zrc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
            producttype=producttype,
        )

        self.zaak = _Zaak.objects.create(
            urn="maykin:openzaak:zrc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
            product=self.product,
        )
        self.taak = _Taak.objects.create(
            urn="maykin:openzaak:trc:taak:d42613cd-ee22-4455-808c-c19c7b8442a1",
            product=self.product,
        )
        self.document = _Document.objects.create(
            urn="maykin:openzaak:drc:document:d42613cd-ee22-4455-808c-c19c7b8442a1",
            product=self.product,
        )

    def test_migration(self):
        self._perform_migration()

        self.urnmappingconfig.refresh_from_db()
        self.assertEqual(self.urnmappingconfig.urn, "urn:nld:maykin:openzaak:zrc:zaak")

        self.zaaktype.refresh_from_db()
        self.assertEqual(
            self.zaaktype.urn,
            "urn:nld:maykin:openzaak:ztc:zaaktype:uuid:1c8cc827-d537-40cd-9558-b5731e240620",
        )

        self.correct_zaaktype.refresh_from_db()
        self.assertEqual(
            self.correct_zaaktype.urn,
            "urn:nld:maykin:openzaak:ztc:zaaktype:uuid:1c8cc827-d537-40cd-9558-b5731e240621",
        )

        self.verzoektype.refresh_from_db()
        self.assertEqual(
            self.verzoektype.urn,
            "urn:nld:maykin:openzaak:vtc:verzoektype:uuid:1c8cc827-d537-40cd-9558-b5731e240621",
        )

        self.proces.refresh_from_db()
        self.assertEqual(
            self.proces.urn,
            "urn:nld:maykin:openzaak:prc:proces:uuid:1c8cc827-d537-40cd-9558-b5731e240622",
        )

        self.product.refresh_from_db()
        self.assertEqual(
            self.product.aanvraag_zaak_urn,
            "urn:nld:maykin:openzaak:zrc:zaak:uuid:d42613cd-ee22-4455-808c-c19c7b8442a1",
        )

        self.zaak.refresh_from_db()
        self.assertEqual(
            self.zaak.urn,
            "urn:nld:maykin:openzaak:zrc:zaak:uuid:d42613cd-ee22-4455-808c-c19c7b8442a1",
        )

        self.taak.refresh_from_db()
        self.assertEqual(
            self.taak.urn,
            "urn:nld:maykin:openzaak:trc:taak:uuid:d42613cd-ee22-4455-808c-c19c7b8442a1",
        )

        self.document.refresh_from_db()
        self.assertEqual(
            self.document.urn,
            "urn:nld:maykin:openzaak:drc:document:uuid:d42613cd-ee22-4455-808c-c19c7b8442a1",
        )
