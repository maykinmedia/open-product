.. _api_index:

==================
API-specifications
==================

.. TODO: standard date

Open Product provides two API, one for **Product**'s and one for **Producttype**'s.
Both of these API's are to be a recommended standard as of ..... The
specifications can be found below.

======================  ==========================================
API                     Specification version(s)
======================  ==========================================
Product API             `0.0.2 <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-product/v0.0.2/src/producten-openapi.yaml>`__
Producttype API         `0.0.2 <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-product/v0.0.2/src/producttypen-openapi.yaml>`__
======================  ==========================================

In addition, Open Product can work with `Notificaties API`_. Open Product uses
`Open Notificaties`_ by default but this can be disabled using ``NOTIFICATIONS_DISABLED`` (see :ref:`installation_env_config`).

REST API design rules
=====================

The Open Product API is compliant with most of the `NLGov REST API Design Rules`_:

Functional rules
----------------

.. list-table:: Functional Rules
    :header-rows: 1

    *   - Rule
        - Compliant
        - Remarks
    *   - `core/naming-resources <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/naming-resources>`_
        - Yes
        -
    *   - `core/naming-collections <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/naming-collections>`_
        - Yes
        -
    *   - `core/interface-language <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/interface-language>`_
        - Yes
        -
    *   - `core/hide-implementation <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/hide-implementation>`_
        - Yes
        -
    *   - `core/http-safety <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/http-safety>`_
        - Yes
        -
    *   - `core/stateless <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/stateless>`_
        - Yes
        -
    *   - `core/nested-child <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/nested-child>`_
        - Yes
        -   - Nested resources are used for translations of producttype & content (READ is done through the normal get action with the Accept-Language header).
            - Prijs, Link and Bestand can only exist in the context of a Producttype but are not nested and have their own endpoint.
            - Other resources that consist of a few fields are done nested within ProductType or Product itself (product document, producttype verzoektype, proces, actie, etc..)
    *   - `core/resource-operations <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/resource-operations>`_
        - Yes
        -
    *   - `core/doc-language <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/doc-language>`_
        - Yes
        -
    *   - `core/deprecation-schedule <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/deprecation-schedule>`_
        - No
        -
    *   - `core/transition-period <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/transition-period>`_
        - No
        - Old docker version are available
    *   - `core/changelog <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/changelog>`_
        - Yes
        - development changelog`_
    *   - `core/geospatial <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/geospatial>`_
        - Yes
        - Not used

Technical rules
---------------

.. list-table:: Technical Rules
    :header-rows: 1

    *   - Rule
        - Compliant
        - Remarks
    *   - `core/no-trailing-slash <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/no-trailing-slash>`_
        - Yes
        -
    *   - `core/http-methods <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/http-methods>`_
        - Yes
        -
    *   - `core/doc-openapi <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/doc-openapi>`_
        - Yes
        - `API spec`_
    *   - `core/publish-openapi <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/publish-openapi>`_
        - Yes
        -
    *   - `core/uri-version <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/uri-version>`_
        - Yes
        -
    *   - `core/semver <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/semver>`_
        - Yes
        -
    *   - `core/version-header <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/version-header>`_
        - Yes
        -
    *   - `core/transport-security <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/transport-security>`_
        - Partially
        - Open Product is missing the headers `Cache-Control: no-store` & `Access-Control-Allow-Origin` from `API Design Rules Module: Transport Security <https://gitdocumentatie.logius.nl/publicatie/api/mod-ts>`_

.. _`Notificaties API`: https://vng-realisatie.github.io/gemma-zaken/standaard/notificaties/
.. _`Open Notificaties`: https://github.com/open-zaak/open-notificaties
.. _`NLGov REST API Design Rules`: https://gitdocumentatie.logius.nl/publicatie/api/adr/
.. _`API spec`: https://github.com/maykinmedia/open-product?tab=readme-ov-file#api-specificatie
