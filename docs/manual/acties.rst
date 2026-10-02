
.. _acties:

Acties
======

Er bestaan 3 verschillende actie typen:

* DMN
* Formulier
* API (experimenteel)

DMN actie
---------
Een dmn actie verwijst naar een externe DMN tabel. In OP kunnen de autorisatie gegevens van externe DMN engines niet worden opgeslagen. De client die de dmn aanroept moet hier zelf voor zorgen.

Om een DMN actie te kunnen toevoegen moet eerst een DMN config worden aangemaakt in de Open Product admin (of via de setup config).
In deze config staat de base url van de dmn engine.

Een DMN actie kan als volgt via de API worden aangemaakt:

.. code-block:: json

    {
        "producttype_uuid": "95792000-d57f-4d3a-b14c-c4c7aa964907",
        "naam": "Parkeervergunning opzegging",
        "type": "dmn",
        "tabel_endpoint": "https://gemeente-a-flowable/dmn-repository/decision-tables",
        "dmn_tabel_id": "46aa6b3a-c0a1-11e6-bc93-6ab56fad108a",
        "mapping": {
            "product": [
                {
                    "name": "pid",
                    "regex": "$.uuid",
                    "classType": "String",
                },
                {
                    "name": "geldigheideinddatum",
                    "regex": "$.eindDatum",
                    "classType": "String",
                },
                {
                    "name": "aantaluren",
                    "regex": "$.verbruiksobject.uren",
                    "classType": "String",
                },
            ],
            "static": [
                {
                    "name": "formulieren",
                    "classType": "String",
                    "value": "https://openformulieren-gemeente-a.nl",
                }
            ],
        },
    }

De DMN url wordt hierdoor ``https://gemeente-a-flowable/dmn-repository/decision-tables/46aa6b3a-c0a1-11e6-bc93-6ab56fad108a``
De mapping van een DMN actie wordt gevalideerd tegen het volgende json schema:

.. literalinclude:: /_generated/dmn_schema.json
   :language: json

Formulier actie
---------------
Een formulier actie kan als volgt via de API worden aangemaakt:

.. code-block:: json

    {
        "producttype_uuid": "95792000-d57f-4d3a-b14c-c4c7aa964907",
        "naam": "Parkeervergunning opzegging",
        "type": "formulier",
        "direct_url": "https://gemeente-a-forms/46aa6b3a-c0a1-11e6-bc93-6ab56fad108a",
        "variabelen": {
            "product": {
                "pid": "$.uuid",
                "geldigheideinddatum": "$.eindDatum",
                "aantaluren": "$.verbruiksobject.uren",
            }
        },
    }

De mapping van een Formulier actie wordt gevalideerd tegen het volgende json schema:

.. literalinclude:: /_generated/form_schema.json
   :language: json

API actie
---------
Een api actie kan als volgt via de API worden aangemaakt:
een api actie gebruikt als enige ook het veld ``method`` om aan te geven of het om een GET of POST request gaat.

.. code-block:: json

    {
        "producttype_uuid": "95792000-d57f-4d3a-b14c-c4c7aa964907",
        "naam": "Parkeervergunning opzegging",
        "type": "api",
        "method": "post",
        "direct_url": "https://gemeente-a-api/46aa6b3a-c0a1-11e6-bc93-6ab56fad108a",
        "mapping": {
            "variabelen": {
                "product": {
                    "pid": "$.uuid",
                    "geldigheideinddatum": "$.eindDatum",
                    "aantaluren": "$.verbruiksobject.uren",
                }
            },
            "static": {"formulieren": "https://openformulieren-gemeente-a.nl"},
        },
    }

De mapping van een API actie wordt gevalideerd tegen het volgende json schema:

.. literalinclude:: /_generated/api_schema.json
   :language: json


.. warning:: Open Product kan de acties niet zelf uitvoeren. Dit betekend dat wijzigingen aan de acties goed moeten worden bijgehouden in Open Producten. Mocht de verwachte post data wijzigen moet de mapping in Open Product dus ook worden gewijzigd.
