from pathlib import Path

from django.test import TestCase

from django_setup_configuration.test_utils import execute_single_step

from openproduct.producttypen.models import ExterneVerwijzingConfig
from openproduct.setup_configuration.steps import (
    ExterneVerwijzingConfigConfigurationStep,
)

CONFIG_FILES = (Path(__file__).parent / "files").resolve()

CONFIG_FILE_PATH = str(CONFIG_FILES / "setup_config_externerverwijzing_config.yaml")


class TestExterneverwijzingConfigStep(TestCase):
    def make_assertions(self):
        config = ExterneVerwijzingConfig.get_solo()

        self.assertEqual(
            config.zaaktypen_url,
            "https://catalogi-api.gemeente.cloud/api/v1/zaaktypen",
        )
        self.assertEqual(
            config.processen_url,
            "https://processen-api.gemeente.cloud/api/v1/processen",
        )
        self.assertEqual(
            config.verzoektypen_url,
            "https://verzoektypen-api.gemeente.cloud/api/v1/verzoektypen",
        )
        self.assertEqual(
            config.documenten_url,
            "https://documenten-api.vng.cloud/api/v1/enkelvoudiginformatieobjecten",
        )

    def test_execute_configuration_step_success(self):

        execute_single_step(
            ExterneVerwijzingConfigConfigurationStep, yaml_source=CONFIG_FILE_PATH
        )

        self.make_assertions()

    def test_execute_configuration_step_update_existing(self):

        config = ExterneVerwijzingConfig.get_solo()
        config.zaaktypen_url = "https://catalogi-api.gemeente.cloud/api/v1/abc"
        config.processen_url = "https://catalogi-api.gemeente.cloud/api/v1/abc"
        config.verzoektypen_url = "https://catalogi-api.gemeente.cloud/api/v1/abc"
        config.documenten_url = "https://catalogi-api.gemeente.cloud/api/v1/abc"
        config.save()

        execute_single_step(
            ExterneVerwijzingConfigConfigurationStep, yaml_source=CONFIG_FILE_PATH
        )

        self.make_assertions()

    def test_execute_configuration_step_idempotent(self):

        execute_single_step(
            ExterneVerwijzingConfigConfigurationStep, yaml_source=CONFIG_FILE_PATH
        )

        self.make_assertions()

        execute_single_step(
            ExterneVerwijzingConfigConfigurationStep, yaml_source=CONFIG_FILE_PATH
        )

        self.make_assertions()
