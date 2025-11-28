from pathlib import Path

from django.test import TestCase

from django_setup_configuration.test_utils import execute_single_step

from openproduct.setup_configuration.steps import (
    UrnMappingConfigsConfigurationStep,
)
from openproduct.urn.models import UrnMappingConfig

CONFIG_FILES = (Path(__file__).parent / "files").resolve()

CONFIG_FILE_PATH = str(CONFIG_FILES / "setup_config_urn_mapping_config.yaml")


class TestDmnConfigStep(TestCase):
    def make_assertions(self):
        self.assertEqual(UrnMappingConfig.objects.all().count(), 2)

        self.assertEqual(
            UrnMappingConfig.objects.get(urn="maykin:abc:ztc:zaak").url,
            "https://maykin.ztc.com/api/v1/zaken",
        )
        self.assertEqual(
            UrnMappingConfig.objects.get(urn="maykin:abc:ztc:taak").url,
            "https://maykin.ztc.com/api/v1/taken",
        )

    def test_execute_configuration_step_success(self):
        execute_single_step(
            UrnMappingConfigsConfigurationStep, yaml_source=CONFIG_FILE_PATH
        )

        self.make_assertions()

    def test_execute_configuration_step_update_existing(self):
        UrnMappingConfig.objects.create(
            urn="maykin:abc:ztc:zaak",
            url="test",
        )

        execute_single_step(
            UrnMappingConfigsConfigurationStep, yaml_source=CONFIG_FILE_PATH
        )

        self.make_assertions()

    def test_execute_configuration_step_idempotent(self):
        execute_single_step(
            UrnMappingConfigsConfigurationStep, yaml_source=CONFIG_FILE_PATH
        )

        self.make_assertions()

        execute_single_step(
            UrnMappingConfigsConfigurationStep, yaml_source=CONFIG_FILE_PATH
        )

        self.make_assertions()
