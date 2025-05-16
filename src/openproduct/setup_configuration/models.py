from django_setup_configuration.models import ConfigurationModel

from openproduct.producttypen.models import ExterneVerwijzingConfig
from openproduct.producttypen.models.dmn_config import DmnConfig


class ExterneVerwijzingConfigConfigurationModel(ConfigurationModel):
    class Meta:
        django_model_refs = {
            ExterneVerwijzingConfig: (
                "naam",
                "basis_url",
                "type",
            )
        }
        extra_kwargs = {
            "naam": {
                "examples": ["documenten api 1"],
                "description": "Name of the externe verwijzing.",
            },
            "basis_url": {
                "examples": [
                    "https://documenten-api.gemeente.cloud/api/v1/enkelvoudiginformatieobjecten"
                ],
                "description": "Base url the externe verwijzing.",
            },
            "type": {
                "examples": ["documenten"],
                "description": "Type of the externe verwijzing. ",  # TODO POSSIBLE VALUES
            },
        }


class ExterneVerwijzingConfigsConfigurationModel(ConfigurationModel):
    configs: list[ExterneVerwijzingConfigConfigurationModel]


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
