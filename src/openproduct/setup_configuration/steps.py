from django_setup_configuration.configuration import BaseConfigurationStep

from openproduct.producttypen.models import ExterneVerwijzingConfig
from openproduct.producttypen.models.dmn_config import DmnConfig
from openproduct.setup_configuration.models import (
    DmnConfigsConfigurationModel,
    ExterneVerwijzingConfigsConfigurationModel,
)


class ExterneVerwijzingConfigsConfigurationStep(BaseConfigurationStep):
    """
    Configure settings for ExterneVerwijzingConfigs
    """

    verbose_name = "ExterneVerwijzingConfig Configuration"
    config_model = ExterneVerwijzingConfigsConfigurationModel
    namespace = "externeverwijzing_config"
    enable_setting = "externeverwijzing_config_enable"

    def execute(self, model: ExterneVerwijzingConfigsConfigurationModel):

        for config in model.configs:
            ExterneVerwijzingConfig.objects.update_or_create(
                naam=config.naam,
                defaults={
                    "basis_url": config.basis_url,
                    "type": config.type,
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
