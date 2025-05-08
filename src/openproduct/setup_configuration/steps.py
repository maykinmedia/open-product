from django_setup_configuration.configuration import BaseConfigurationStep

from openproduct.producttypen.models import ExterneVerwijzingConfig
from openproduct.producttypen.models.dmn_config import DmnConfig
from openproduct.setup_configuration.models import (
    DmnConfigsConfigurationModel,
    ExterneVerwijzingConfigConfigurationModel,
)


class ExterneVerwijzingConfigConfigurationStep(BaseConfigurationStep):
    """
    Configure settings for ExterneVerwijzingConfig
    """

    verbose_name = "ExterneVerwijzingConfig Configuration"
    config_model = ExterneVerwijzingConfigConfigurationModel
    namespace = "externeverwijzing_config"
    enable_setting = "externeverwijzing_config_enable"

    def execute(self, model: ExterneVerwijzingConfigConfigurationModel):
        config = ExterneVerwijzingConfig.get_solo()

        if model.zaaktypen_url:
            config.zaaktypen_url = model.zaaktypen_url

        if model.processen_url:
            config.processen_url = model.processen_url

        if model.verzoektypen_url:
            config.verzoektypen_url = model.verzoektypen_url

        if model.documenten_url:
            config.documenten_url = model.documenten_url

        config.save()


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

            dmn_config_qs = DmnConfig.objects.filter(
                tabel_endpoint=config.tabel_endpoint
            )
            if dmn_config_qs.exists():
                dmn_config = dmn_config_qs.get()
                dmn_config.naam = config.naam
                dmn_config.save()

            else:
                DmnConfig.objects.create(
                    naam=config.naam,
                    tabel_endpoint=config.tabel_endpoint,
                )
