from pathlib import Path

from django.test import TestCase

from django_setup_configuration.test_utils import execute_single_step

from openproduct.producttypen.models.dmn_config import DmnConfig
from openproduct.setup_configuration.steps import DmnConfigsConfigurationStep

CONFIG_FILES = (Path(__file__).parent / "files").resolve()

CONFIG_FILE_PATH = str(CONFIG_FILES / "setup_config_dmn_config.yaml")


class TestDmnConfigStep(TestCase):
    def make_assertions(self):

        self.assertEqual(DmnConfig.objects.all().count(), 2)

        self.assertEqual(
            DmnConfig.objects.get(naam="main repository").tabel_endpoint,
            "https://gemeente.flowable-dmn.nl/flowable-rest/dmn-api/dmn-repository/",
        )
        self.assertEqual(
            DmnConfig.objects.get(naam="new repository").tabel_endpoint,
            "https://new.flowable-dmn.nl/flowable-rest/dmn-api/dmn-repository/",
        )

    def test_execute_configuration_step_success(self):

        execute_single_step(DmnConfigsConfigurationStep, yaml_source=CONFIG_FILE_PATH)

        self.make_assertions()

    def test_execute_configuration_step_update_existing(self):

        DmnConfig.objects.create(
            tabel_endpoint="https://gemeente.flowable-dmn.nl/flowable-rest/dmn-api/dmn-repository/",
            naam="test",
        )

        execute_single_step(DmnConfigsConfigurationStep, yaml_source=CONFIG_FILE_PATH)

        self.make_assertions()

    def test_execute_configuration_step_idempotent(self):

        execute_single_step(DmnConfigsConfigurationStep, yaml_source=CONFIG_FILE_PATH)

        self.make_assertions()

        execute_single_step(DmnConfigsConfigurationStep, yaml_source=CONFIG_FILE_PATH)

        self.make_assertions()
