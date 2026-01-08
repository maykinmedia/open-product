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
            url="https://processen.maykin.nl/processen", urn="maykin:abc:ptc:proces"
        )
        UrnMappingConfig.objects.create(
            url="https://verzoektypen.maykin.nl/verzoektypen",
            urn="maykin:abc:vtc:verzoektype",
        )
        UrnMappingConfig.objects.create(
            url="https://zaaktypen.maykin.nl/zaaktypen", urn="maykin:abc:ztc:zaaktype"
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
            "maykin:abc:ztc:zaaktype:1c8cc827-d537-40cd-9558-b5731e240620",
        )
        self.assertEqual(
            VerzoekType.objects.get().urn,
            "maykin:abc:vtc:verzoektype:1c8cc827-d537-40cd-9558-b5731e240621",
        )
        self.assertEqual(
            Proces.objects.get().urn,
            "maykin:abc:ptc:proces:1c8cc827-d537-40cd-9558-b5731e240622",
        )
