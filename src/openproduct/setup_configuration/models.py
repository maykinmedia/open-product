from django_setup_configuration import DjangoModelRef
from django_setup_configuration.models import ConfigurationModel

from openproduct.producttypen.models.dmn_config import DmnConfig
from openproduct.urn.models import UrnMappingConfig


class UrnMappingConfigConfigurationModel(ConfigurationModel):
    urn: str = DjangoModelRef(UrnMappingConfig, "urn")
    url: str = DjangoModelRef(UrnMappingConfig, "url")

    class Meta:
        # django_model_refs = {
        #     UrnMappingConfig: (
        #         "urn",
        #         "url"
        #     )
        # }

        extra_kwargs = {
            "urn": {
                "examples": ["https://urn.gemeente.cloud/api/v1/urn"],
                "description": "Base url of the urn API.",
            },
            "url": {
                "examples": ["https://url-api.gemeente.cloud/api/v1/url"],
                "description": "Base url of the urn API.",
            },
        }


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
