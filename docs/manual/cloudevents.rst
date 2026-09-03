.. _cloudevents_docs:

CloudEvents
===========

.. warning::

    Deze events zijn nog in ontwikkeling, en kunnen dus nog worden gewijzigd in toekomstige versies.
    Het is nog niet aanbevolen om dit in productie te gebruiken.

`CloudEvents <https://cloudevents.io/>`_ is een specificatie voor het op een gemeenschappelijke manier
beschrijven van data. Open Product ondersteunt het versturen van events via de Notificaties-API:

* ``nl.overheid.zaken.zaak-gekoppeld``: wordt verstuurd wanneer een product wordt aangemaakt en wanneer
  de gekoppelde zaak van een product (``aanvraag_zaak``) wordt aangepast.
* ``nl-overheid-zaken.zaak-ontkoppeld``: wordt verstuurd wanneer een product wordt verwijderd en wanneer
  de gekoppelde zaak van een product (``aanvraag_zaak``) wordt aangepast.
* ``nl-overheid-zaken.zaakobject-einddatum-bijgewerkt``: wordt verstuurd wanneer een product wordt
  aangemaakt en verwijderd, en wanneer de einddatum van een product wordt aangepast.

Configuratie
------------

1. De events worden alleen verstuurd wanneer de volgende omgevingsvariabelen (zie ook :ref:`installation_env_config`)
   zijn geconfigureerd:

   * ``ENABLE_CLOUD_EVENTS``: moet op ``True`` staan.
   * ``NOTIFICATIONS_SOURCE``: mag geen lege string bevatten. Gebruik de identificatiecode van deze
     applicatie, bijvoorbeeld ``urn:nld:oin:000919673854:openproduct``.

2. Zorg ervoor dat de verbinding met Open Notificaties is gemaakt (zie ook :ref:`installation_configuration_notificaties_api`).

Voorbeelden
-----------

Voorbeeld van een ``nl.overheid.zaken.zaak-gekoppeld``-event:

.. code-block:: json

    {
        "specversion": "1.0",
        "type": "nl.overheid.zaken.zaak-gekoppeld",
        "source": "urn:nld:oin:000919673854:openproduct",
        "subject": "2cb84d34-74a6-4515-bd12-6d50f45d45b5",
        "id": "da720942-75e0-4731-a097-1b181af57476",
        "time": "2026-08-25T10:00:00Z",
        "datacontenttype": "application/json",
        "data": {
            "zaak": "https//open-zaak.local.nl/api/v1/zaken/2cb84d34-74a6-4515-bd12-6d50f45d45b5",
            "linkTo": "https://open-product.local.nl/producten/api/v1/producten/c1e18e83-c3e3-44a6-b457-48845a8946c4",
            "label": "Vergunning instantie.",
            "linkObjectType": "product"
        }
    }

Voorbeeld van een ``nl.overheid.zaken.zaak-ontkoppeld``-event:

.. code-block:: json

    {
        "specversion": "1.0",
        "type": "nl.overheid.zaken.zaak-ontkoppeld",
        "source": "urn:nld:oin:000919673854:openproduct",
        "subject": "2cb84d34-74a6-4515-bd12-6d50f45d45b5",
        "id": "e288a395-b60f-42be-b792-f3c04272794a",
        "time": "2026-08-25T10:00:00Z",
        "datacontenttype": "application/json",
        "data": {
            "zaak": "https//open-zaak.local.nl/api/v1/zaken/2cb84d34-74a6-4515-bd12-6d50f45d45b5",
            "linkTo": "https://open-product.local.nl/producten/api/v1/producten/c1e18e83-c3e3-44a6-b457-48845a8946c4",
        }
    }

Voorbeeld van een ``nl.overheid.zaken.zaakobject-einddatum-bijgewerkt``-event:

.. code-block:: json

    {
        "specversion": "1.0",
        "type": "nl.overheid.zaken.zaakobject-einddatum-bijgewerkt",
        "source": "urn:nld:oin:000919673854:openproduct",
        "subject": "2cb84d34-74a6-4515-bd12-6d50f45d45b5",
        "id": "06b597b2-d65c-46d5-8655-dd6bd7e2e5f9",
        "time": "2026-08-25T10:00:00Z",
        "datacontenttype": "application/json",
        "data": {
            "zaak": "https//open-zaak.local.nl/api/v1/zaken/2cb84d34-74a6-4515-bd12-6d50f45d45b5",
        }
    }

Merk op dat in alle gevallen het ``subject``-veld de UUID van de Zaak bevat. Voor het ontkoppelen van zaken zijn
een ``label`` en ``linkObjectType`` niet nodig in de data.
