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

The Open Product API is compliant with most of the `NLGov REST API Design Rules`_:

Functional rules
----------------

- `core/naming-resources <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/naming-resources>`_
- `core/naming-collections <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/naming-collections>`_
- `core/interface-language <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/interface-language>`_
- `core/hide-implementation <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/hide-implementation>`_
- `core/http-safety <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/http-safety>`_
- `core/stateless <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/stateless>`_
- `core/nested-child <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/nested-child>`_
- `core/resource-operations <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/resource-operations>`_
- `core/doc-language <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/doc-language>`_
- `core/deprecation-schedule <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/deprecation-schedule>`_
    - TODO
- `core/transition-period <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/transition-period>`_
    - TODO
- `core/changelog <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/changelog>`_
- `core/geospatial <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/geospatial>`_ (not used)

Technical rules
---------------

- `core/no-trailing-slash <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/no-trailing-slash>`_
- `core/http-methods <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/http-methods>`_
- `core/doc-openapi <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/doc-openapi>`_
- `core/publish-openapi <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/publish-openapi>`_
- `core/uri-version <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/uri-version>`_
- `core/semver <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/semver>`_
- `core/version-header <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/version-header>`_
- `core/transport-security <https://gitdocumentatie.logius.nl/publicatie/api/adr/2.0.2/#/core/transport-security>`_
    - TODO

.. _`Notificaties API`: https://vng-realisatie.github.io/gemma-zaken/standaard/notificaties/
.. _`Open Notificaties`: https://github.com/open-zaak/open-notificaties
.. _`NLGov REST API Design Rules`: https://gitdocumentatie.logius.nl/publicatie/api/adr/
