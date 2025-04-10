.. _manual_oidc:

===========================
OpenID Connect configureren
===========================

Open Product ondersteunt Single Sign On (SSO) via het OpenID Connect protocol (OIDC) voor de beheerinterface.

Gebruikers kunnen op die manier inloggen op Open Product met hun account bij de OpenID Connect provider. In deze
flow:

1. Klikt een gebruiker op het inlogscherm op *Inloggen met OIDC*
2. De gebruiker wordt naar de omgeving van de OpenID Connect provider geleid (bijv. Keycloak) waar ze inloggen met gebruikersnaam
   en wachtwoord (en eventuele Multi Factor Authentication)
3. De OIDC omgeving stuurt de gebruiker terug naar Open Product (waar de account aangemaakt
   wordt indien die nog niet bestaat)
4. Een beheerder in Open Product kent de juiste groepen toe aan deze gebruiker als deze
   voor het eerst inlogt.

.. note:: Standaard krijgen deze gebruikers **geen** toegang tot de beheerinterface. Deze
   rechten moeten door een (andere) beheerder :ref:`ingesteld <manual_users>` worden. De
   account is wel aangemaakt.

.. _manual_oidc_appgroup:

Daarnaast kan een JWT token van de OpenID provider worden gebruikt om the authenticeren voor de API.

Configureren van OIDC zelf
==========================

Contacteer de IAM beheerders in je organisatie om een *Client* aan te
maken in de omgeving van de OpenID Connect provider.

Voor de **Redirect URI** vul je ``https://open-product.gemeente.nl/oidc/callback`` in,
waarbij je ``open-product.gemeente.nl`` vervangt door het relevante domein.

Aan het eind van dit proces moet je de volgende gegevens hebben (on premise):

* Server adres, bijvoorbeeld ``login.gemeente.nl``
* Client ID, bijvoorbeeld ``a7d14516-8b20-418f-b34e-25f53c930948``
* Client secret, bijvoorbeeld ``97d663a9-3624-4930-90c7-2b90635bd990``

Configureren van OIDC in Open Product
=======================================

Zorg dat je de volgende :ref:`gegevens <manual_oidc_appgroup>` hebt:

* Server adres
* Client ID
* Client secret

Navigeer vervolgens in de admin naar **Configuratie** > **OpenID Connect configuration**.

1. Vink *Enable* aan om OIDC in te schakelen.
2. Vul bij **OpenID Connect client ID** het Client ID in, bijvoorbeeld
   ``a7d14516-8b20-418f-b34e-25f53c930948``.
3. Vul bij **OpenID Connect secret** het Client secret in, bijvoobeeld
   ``97d663a9-3624-4930-90c7-2b90635bd990``.
4. Laat bij **OpenID Connect scopes** de standaardwaarden staan.
5. Vul bij **OpenID sign algorithm** ``RS256`` in.
6. Laat **Sign key** leeg.

Vervolgens moeten er een aantal endpoints van de OIDC provider ingesteld worden,
deze kunnen automatisch bepaald worden aan de hand van het discovery endpoint
(``https://login.gemeente.nl/auth/realms/{realm}/.well-known/openid-configuration``).

7. Vul bij **Discovery endpoint** het pad naar het juiste authenticatie realm endpoint
   van de OpenID Connect provider in (met een ``/`` op het einde). Voor provider-specifieke
   hints, zie :ref:`manual_oidc_providers`.
8. Laat de overige endpoints leeg.

Klik tot slot rechtsonder op **Opslaan**.

Je kan vervolgens het makkelijkst testen of alles werkt door in een incognitoscherm
naar https://open-product.gemeente.nl/admin/ te navigeren en op *Inloggen met OIDC* te
klikken.

.. _manual_oidc_providers:

Providersreferentie
===================

Azure AD
--------

Azure Active Directory is a cloud-hosted identity provider from Microsoft, part of Azure webservices.

To use AAD as OIDC provider, you require a Tenant ID, usually in the same of a UUID v4.
This tenant ID is used in the discovery URL, having the form
``https://login.microsoftonline.com/${tenantId}/v2.0``.

Keycloak
--------

Keycloak is a multi-tenant IDP which itself can configure other IDPs.

To use Keycloak, you need to know your relevant ``realm``. The discovery URL has the form
``https://keycloak.gemeente.nl/auth/realms/${realm}/.well-known/openid-configuration``.
