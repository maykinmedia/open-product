import structlog
from django_setup_configuration.configuration import BaseConfigurationStep
from django_setup_configuration.exceptions import ConfigurationRunFailed
from zgw_consumers.models import Service

from openproduct.config.models import ReferentielijstenConfig
from openproduct.producttypen.models.dmn_config import DmnConfig
from openproduct.setup_configuration.models import (
    DmnConfigsConfigurationModel,
    ReferentielijstenConfigurationModel,
    UrnMappingConfigsConfigurationModel,
)
from openproduct.urn.models import UrnMappingConfig

logger = structlog.stdlib.get_logger(__name__)


def get_service(slug: str) -> Service:
    """
    Try to find a Service and re-raise DoesNotExist with the identifier to make debugging
    easier
    """
    try:
        return Service.objects.get(slug=slug)
    except Service.DoesNotExist as e:
        raise Service.DoesNotExist(f"{str(e)} (identifier = {slug})")


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


class ReferentielijstenConfigurationStep(
    BaseConfigurationStep[ReferentielijstenConfigurationModel]
):
    namespace = "referentielijsten_config"
    enable_setting = "referentielijsten_config_enable"

    verbose_name = "Configuration for Referentielijsten service"
    config_model = ReferentielijstenConfigurationModel

    def execute(self, model: ReferentielijstenConfigurationModel) -> None:
        logger.info(
            "configuring_referentielijsten",
            enabled=model.enabled,
            service_identifier=model.referentielijsten_api_service_identifier,
        )

        service = None
        if identifier := model.referentielijsten_api_service_identifier:
            try:
                service = get_service(identifier)
            except Service.DoesNotExist as exc:
                logger.warning("referentielijsten_configuration_failure")
                raise ConfigurationRunFailed(
                    f"Could not find Service with identifier '{identifier}'. "
                    "Ensure the ServiceConfigurationStep has been run successfully."
                ) from exc

        config_instance = ReferentielijstenConfig.get_solo()
        config_instance.enabled = model.enabled
        config_instance.service = service

        config_instance.kanalen_tabel_code = model.kanalen_tabel_code

        config_instance.save()

        logger.info("referentielijsten_configuration_success")
