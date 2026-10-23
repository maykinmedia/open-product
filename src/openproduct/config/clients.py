from referentielijsten_api_client.client import ReferentielijstenClient
from zgw_consumers.client import build_client

from .exceptions import NoServiceConfigured


def get_referentielijsten_client(
    config: ReferentielijstenClient,
) -> ReferentielijstenClient:
    if not config.service:
        raise NoServiceConfigured("No Referentielijsten API service configured!")

    return build_client(config.service, client_factory=ReferentielijstenClient)
