============
Open Product
============

:Version: 0.0.5
:Source: https://github.com/maykinmedia/open-product
:Keywords: ``products``

Place for municipalities to manage product types and products to be able to use them in other applications.
(`Nederlandse versie`_)

Developed by `Maykin B.V.`_.


Introduction
============

Open Product is an application where product types and products can be managed in a single place.
Other applications like Open Inwoner and Open Formulieren can integrate Open Product using its REST API to for example show product type information, create products or to get the current price for a product type.

This Project is currently in the development fase.

Open Product can store Product types and products, A product type is for example a parking permit and contains all relevant information such as what the rules are and how different parking zones work etc.
A product in this example is a parking permit of a person and contains in this instance the license plate and personal information.

Information Model
=================

.. image:: docs/introduction/assets/open-product-informatiemodel-diagram.png
   :alt: Open Product informatiemodel


API specification
=================

|lint-oas| |generate-sdks| |generate-postman-collection|

==============  ==============  =============================
Version         Release date    API specification
==============  ==============  =============================
latest          n/a             `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-product/main/src/openproduct/api/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-product/main/src/openproduct/api/openapi.yaml>`_
==============  ==============  =============================

There a two ways to connect to authenticate with the API:

* An api token can be created in the Open Product admin -> Users -> Tokens.
* OpenId Connect can be configured in the Open Product admin -> Config -> OpenID connect configuration.



See: `All versions and changes <https://github.com/maykinmedia/open-product/blob/main/CHANGELOG.rst>`_


Developers
==========

|build-status| |coverage| |black| |python-versions|

This repository contains the source code for openproduct. To quickly
get started, we recommend using the Docker image. You can also build the
project from the source code. For this, please look at
`INSTALL.rst <INSTALL.rst>`_.

Open Product consists of three apps:

* product types
* products
* locations (& organisations)


Quickstart
----------

1. Download and run openproduct:

   .. code:: bash

      $ wget https://raw.githubusercontent.com/maykinmedia/open-product/main/docker-compose.yml
      $ docker-compose up -d --no-build
      $ docker-compose exec web src/manage.py loaddata demodata
      $ docker-compose exec web src/manage.py createsuperuser

2. In the browser, navigate to ``http://localhost:8000/`` to access the admin
   and the API.


References
==========

* `Documentation <https://open-product.readthedocs.io/en/stable/>`_
* `Docker image <https://hub.docker.com/r/maykinmedia/open-product>`_
* `Issues <https://github.com/maykinmedia/open-product/issues>`_
* `Code <https://github.com/maykinmedia/open-product>`_
* `Community <https://TODO>`_


License
=======

Copyright © Maykin 2024

Licensed under the EUPL_


.. _`Nederlandse versie`: README.rst

.. _`Maykin B.V.`: https://www.maykinmedia.nl

.. _`EUPL`: LICENSE.md

.. |build-status| image:: https://github.com/maykinmedia/open-product/workflows/ci/badge.svg?branch=main
    :alt: Build status
    :target: https://github.com/maykinmedia/open-product/actions?query=workflow%3Aci

.. |coverage| image:: https://codecov.io/github/maykinmedia/open-roducten/branch/main/graphs/badge.svg?branch=main
    :alt: Coverage
    :target: https://codecov.io/gh/maykinmedia/open-product

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :alt: Code style
    :target: https://github.com/psf/black

.. |python-versions| image:: https://img.shields.io/badge/python-3.11%2B-blue.svg
    :alt: Supported Python version

.. |lint-oas| image:: https://github.com/maykinmedia/open-product/workflows/lint-oas/badge.svg
    :alt: Lint OAS
    :target: https://github.com/maykinmedia/open-product/actions?query=workflow%3Alint-oas

.. |generate-sdks| image:: https://github.com/maykinmedia/open-product/workflows/generate-sdks/badge.svg
    :alt: Generate SDKs
    :target: https://github.com/maykinmedia/open-product/actions?query=workflow%3Agenerate-sdks

.. |generate-postman-collection| image:: https://github.com/maykinmedia/open-product/workflows/generate-postman-collection/badge.svg
    :alt: Generate Postman collection
    :target: https://github.com/maykinmedia/open-product/actions?query=workflow%3Agenerate-postman-collection
