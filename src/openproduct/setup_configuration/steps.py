from django_setup_configuration.configuration import BaseConfigurationStep

from openproduct.producttypen.models.dmn_config import DmnConfig
from openproduct.setup_configuration.models import (
    DmnConfigsConfigurationModel,
    UrnMappingConfigsConfigurationModel,
)
from openproduct.urn.models import UrnMappingConfig


class UrnMappingConfigsConfigurationStep(BaseConfigurationStep):
    """
    Configure settings for UrnMappingConfig
    """

    verbose_name = "UrnMapping Configuration"
    config_model = UrnMappingConfigsConfigurationModel
    namespace = "urn_mapping_config"
    enable_setting = "urn_mapping_config_enable"

    def execute(self, model: UrnMappingConfigsConfigurationModel) -> None:
        for config in model.configs:
            UrnMappingConfig.objects.update_or_create(
                urn=config.urn,
                defaults={
                    "url": config.url,
                },
            )


class DmnConfigsConfigurationStep(BaseConfigurationStep):
    """
    Configure settings for DmnConfigs
    """

    verbose_name = "DmnConfig Configuration"
    config_model = DmnConfigsConfigurationModel
    namespace = "dmn_config"
    enable_setting = "dmn_config_enable"

    def execute(self, model: DmnConfigsConfigurationModel) -> None:
        for config in model.configs:
            DmnConfig.objects.update_or_create(
                tabel_endpoint=config.tabel_endpoint,
                defaults={
                    "naam": config.naam,
                },
            )
