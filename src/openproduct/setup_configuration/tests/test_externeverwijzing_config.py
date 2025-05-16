from pathlib import Path

from django.test import TestCase

from django_setup_configuration.test_utils import execute_single_step

from openproduct.producttypen.models import ExterneVerwijzingConfig
from openproduct.setup_configuration.steps import (
    ExterneVerwijzingConfigsConfigurationStep,
)

CONFIG_FILES = (Path(__file__).parent / "files").resolve()

CONFIG_FILE_PATH = str(CONFIG_FILES / "setup_config_externerverwijzing_config.yaml")


class TestExterneverwijzingConfigStep(TestCase):
    def make_assertions(self):
        self.assertEqual(ExterneVerwijzingConfig.objects.all().count(), 2)

        self.assertEqual(
            ExterneVerwijzingConfig.objects.get(naam="documenten api 1").basis_url,
            "https://documenten-api.gemeente.cloud/api/v1/enkelvoudiginformatieobjecten",
        )
        self.assertEqual(
            ExterneVerwijzingConfig.objects.get(naam="zaaktypen api 1").basis_url,
            "https://catalogi-api.gemeente.cloud/api/v1/zaaktypen",
        )

    def test_execute_configuration_step_success(self):
        execute_single_step(
            ExterneVerwijzingConfigsConfigurationStep, yaml_source=CONFIG_FILE_PATH
        )

        self.make_assertions()

    def test_execute_configuration_step_update_existing(self):
        ExterneVerwijzingConfig.objects.create(
            basis_url="https://google.com",
            naam="documenten api 1",
        )

        execute_single_step(
            ExterneVerwijzingConfigsConfigurationStep, yaml_source=CONFIG_FILE_PATH
        )

        self.make_assertions()

    def test_execute_configuration_step_idempotent(self):
        execute_single_step(
            ExterneVerwijzingConfigsConfigurationStep, yaml_source=CONFIG_FILE_PATH
        )

        self.make_assertions()

        execute_single_step(
            ExterneVerwijzingConfigsConfigurationStep, yaml_source=CONFIG_FILE_PATH
        )

        self.make_assertions()
