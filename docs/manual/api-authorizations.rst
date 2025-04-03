.. _manual_api_auth:

==================
API-toegang beheer
==================

De API's die Open Producten aanbied zijn niet toegankelijk
zonder authenticatie en autorisatie - gegevens worden namelijk correct beveiligd.

Voordat een applicatie dus gegevens kan opvragen, opvoeren, bewerken of vernietigen,
moet deze applicatie hiervoor bekend zijn en geautoriseerd zijn.

.. _manual_generate_token:

Een Token genereren voor API-toegang
================================================

Je kan de applicatie waarvan je autorisaties wenst in te stellen bereiken via het
de beheer omgeving van de Open Producten. Binnen de beheer omgeving kan men onder
de menu optie **Users** de link **Tokens** vinden. Deze link lijdt naar de lijstweergave
van alle aangemaakte Tokens waarmee toegang mogelijk is naar de API's van Open Producten.

Om een nieuwe Token aan te maken klikt de gebruiker op de knop **TOKEN TOEVOEGEN**.
Hier kan vervolgens een gebruiker gekozen worden waaraan de Token is gekoppeld.
Tenslotte wordt er wanneer er op de knop **Opslaan** wordt geklikt een Token gegenereerd
en wordt deze getoond op het scherm waarnaar de gebruiker wordt verwezen.

.. _manual_use_oidc:

Een JWT token gebruiken van een OIDC provider voor API-toegang
===============================================================

Nadat de openID connect is :ref:`geconfigureerd <manual_oidc>` kunnen jwt tokens van de openID provider worden gebruikt voor toegang tot de API.


