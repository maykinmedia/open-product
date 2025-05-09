from django_setup_configuration.models import ConfigurationModel

from openproduct.producttypen.models import ExterneVerwijzingConfig
from openproduct.producttypen.models.dmn_config import DmnConfig


class ExterneVerwijzingConfigConfigurationModel(ConfigurationModel):
    class Meta:
        django_model_refs = {
            ExterneVerwijzingConfig: (
                "zaaktypen_url",
                "processen_url",
                "verzoektypen_url",
                "documenten_url",
            )
        }
        extra_kwargs = {
            "zaaktypen_url": {
                "examples": ["https://catalogi-api.gemeente.cloud/api/v1/zaaktypen"],
                "description": "Base url of the zaaktypen API.",
            },
            "processen_url": {
                "examples": ["https://processen-api.gemeente.cloud/api/v1/processen"],
                "description": "Base url of processen.",
            },
            "verzoektypen_url": {
                "examples": [
                    "https://verzoektypen-api.gemeente.cloud/api/v1/verzoektypen"
                ],
                "description": "Base url of the verzoektypen.",
            },
            "documenten_url": {
                "examples": [
                    "https://documenten-api.gemeente.cloud/api/v1/enkelvoudiginformatieobjecten"
                ],
                "description": "Base url of the Documenten API.",
            },
        }


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
