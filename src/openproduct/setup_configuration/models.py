from django_setup_configuration import DjangoModelRef
from django_setup_configuration.models import ConfigurationModel

from openproduct.config.models import ReferentielijstenConfig
from openproduct.producttypen.models.dmn_config import DmnConfig
from openproduct.urn.models import UrnMappingConfig


class UrnMappingConfigConfigurationModel(ConfigurationModel):
    urn: str = DjangoModelRef(
        UrnMappingConfig,
        "urn",
        examples=["urn:nld:maykin:openzaak:ztc:zaak"],
        description="Base urn (<organisatie>:<systeem>:<component>:<resource>)",
    )
    url: str = DjangoModelRef(
        UrnMappingConfig,
        "url",
        examples=["https://gemeente-a.zgw.nl/zaken"],
        description="Base url of the urn.",
    )


class UrnMappingConfigsConfigurationModel(ConfigurationModel):
    configs: list[UrnMappingConfigConfigurationModel]


class DmnConfigConfigurationModel(ConfigurationModel):
    class Meta:
        django_model_refs = {
            DmnConfig: (
                "naam",
                "tabel_endpoint",
            )
        }
        extra_kwargs = {
            "naam": {
                "examples": ["main repository"],
                "description": "Name of the DMN instance",
            },
            "tabel_endpoint": {
                "examples": [
                    "https://gemeente.flowable-dmn.nl/flowable-rest/dmn-api/dmn-repository/"
                ],
                "description": "Base url of the DMN instance.",
            },
        }


class DmnConfigsConfigurationModel(ConfigurationModel):
    configs: list[DmnConfigConfigurationModel]


class ReferentielijstenConfigurationModel(ConfigurationModel):
    referentielijsten_api_service_identifier: str = DjangoModelRef(
        ReferentielijstenConfig, "service"
    )

    class Meta:
        django_model_refs = {
            ReferentielijstenConfig: [
                "enabled",
                "kanalen_tabel_code",
            ]
        }

        extra_kwargs = {
            "referentielijsten_api_service_identifier": {
                "examples": ["referentielijsten-api"]
            },
        }
