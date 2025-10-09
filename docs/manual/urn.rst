
.. _urns:

Urns
====

syntax
------

``<organisatie>:<systeem>:<component>:<resource>:<identificatie>``

``maykin:zaken-sociaal:zrc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1``

.. note::
    Houd het systeem-fragment leverancier en product agnostisch. Een afdeling of domein zou bijvoorbeeld wel kunnen.

Transitie
---------

Om geleidelijk te kunnen overstappen van urls naar urns worden voor nu beide ondersteund.
Door een urn mapping aan te maken kan een relatie worden gelegd tussen een basis urn en een basis url. Zo hoeft via de admin of API alleen de urn of url worden ingevuld.

Via de settings ``REQUIRE_URL_URN_MAPPING`` & ``REQUIRE_URN_URL_MAPPING`` kan worden ingesteld of er een error moet worden teruggegeven als er geen mapping bestaat. (beide staan standaard aan)

Voorbeeld
---------

De product aanvraag_zaak is de link naar de zaak waaruit het product is afgeleid. Product heeft twee velden ``aanvraag_zaak_urn`` & ``aanvraag_zaak_url``

- De volgende urn mapping is toegevoegd: maykin:zaken-sociaal:zrc:zaak -> https://maykin.zrc.com/api/v1/zaken
- Een product kan worden aangemaakt met bijvoorbeeld de urn ``maykin:zaken-sociaal:zrc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1`` of url ``https://maykin.zrc.com/api/v1/zaken/d42613cd-ee22-4455-808c-c19c7b8442a1`` waarna de ander vanuit de urn mapping automatisch wordt ingevuld.
- Open Product heeft verder geen authenticatie gegevens van in dit geval een Open Zaak instantie en doet verder geen validatie, dit is een taak van de clients.
