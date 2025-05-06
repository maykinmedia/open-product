from django_setup_configuration.models import ConfigurationModel

from openproduct.producttypen.models import ExterneVerwijzingConfig


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
                "examples": ["https://catalogi-api.gemeente.cloud/api/v1/zaaktypen"]
            },
            "processen_url": {
                "examples": ["https://processen-api.gemeente.cloud/api/v1/processen"]
            },
            "verzoektypen_url": {
                "examples": [
                    "https://verzoektypen-api.gemeente.cloud/api/v1/verzoektypen"
                ]
            },
            "documenten_url": {
                "examples": [
                    "https://documenten-api.gemeente.cloud/api/v1/enkelvoudiginformatieobjecten"
                ]
            },
        }
