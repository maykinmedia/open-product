from django.conf import settings
from django.db import transaction

from notifications_api_common.cloudevents import process_cloudevent

from .models import Product

ZAAK_GEKOPPELD = "nl.overheid.zaken.zaak-gekoppeld"
ZAAK_ONTKOPPELD = "nl.overheid.zaken.zaak-ontkoppeld"
ZAAKOBJECT_EINDDATUM_BIJGEWERKT = "nl.overheid.zaken.zaakobject-einddatum-bijgewerkt"


def _get_zaak_uri(product: Product):
    if product.aanvraag_zaak_url:
        return product.aanvraag_zaak_url
    else:
        # TODO: Open Zaak cannot handle urns that end with 'uuid' and have arbitrary namespaces,
        #  so we reconstruct into the standardized urn:uuid namespace. Question: should OZ be able
        #  to handle this?
        return f"urn:uuid:{product.zaak_uuid}"


def send_zaak_gekoppeld_cloudevent(product: Product, link_to: str):
    """
    Send a ZAAK_GEKOPPELD cloudevent with transaction handling (only runs on commit).

    :param product: Relevant product.
    :param link_to: Full URL to the product.
    """
    if not settings.ENABLE_CLOUD_EVENTS:
        return

    transaction.on_commit(
        lambda: process_cloudevent(
            event_type=ZAAK_GEKOPPELD,
            subject=product.zaak_uuid,
            data={
                "zaak": _get_zaak_uri(product),
                "linkTo": link_to,
                "label": str(product),
                "linkObjectType": "product",
            },
        )
    )


def send_zaak_ontkoppeld_cloudevent(product: Product, link_to: str):
    """
    Send a ZAAK_ONTKOPPELD cloudevent with transaction handling (only runs on commit).

    :param product: Relevant product.
    :param link_to: Full URL to the product.
    """
    if not settings.ENABLE_CLOUD_EVENTS:
        return

    transaction.on_commit(
        lambda: process_cloudevent(
            event_type=ZAAK_ONTKOPPELD,
            subject=product.zaak_uuid,
            data={
                "zaak": _get_zaak_uri(product),
                "linkTo": link_to,
                # label and linkObjectType are not used for unlinking
            },
        )
    )


def send_einddatum_bijgewerkt_cloudevent(product: Product):
    """
    Send a PRODUCT_EINDDATUM_BIJGEWERKT cloudevent with transaction handling
    (only runs on commit).

    :param product: Relevant product.
    """
    if not settings.ENABLE_CLOUD_EVENTS:
        return

    transaction.on_commit(
        lambda: process_cloudevent(
            event_type=ZAAKOBJECT_EINDDATUM_BIJGEWERKT,
            subject=product.zaak_uuid,
            data={"zaak": _get_zaak_uri(product)},
        )
    )
