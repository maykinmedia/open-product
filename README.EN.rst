============
Open Product
============

:Version: 1.5.0
:Source: https://github.com/maykinmedia/open-product
:Keywords: ``products``

Place for municipalities to manage product types and products to be able to use them in other applications.
(`Nederlandse versie`_)

Developed by `Maykin B.V.`_.


Introduction
============

Open Product is an application where product types and products can be managed in a single place.
Other applications like Open Inwoner and Open Formulieren can integrate Open Product using its REST API to for example show product type information, create products or to get the current price for a product type.

Open Product can store Product types and products, A product type is for example a parking permit and contains all relevant information such as what the rules are and how different parking zones work etc.
A product in this example is a parking permit of a person and contains in this instance the license plate and personal information.

Information Model
=================

.. image:: docs/introduction/assets/open-product-informatiemodel-diagram.png
   :alt: Open Product informatiemodel


API specification
=================

Products
--------

==============  ==============  =============================
API version     Release date    API specification
==============  ==============  =============================
latest          n/a             `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-product/master/src/producten-openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-product/master/src/producten-openapi.yaml>`_,
                                (`diff <https://github.com/maykinmedia/open-product/compare/1.5.0..master>`_)
1.4.0           2025-12-04      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.5.0/src/producten-openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.5.0/src/producten-openapi.yaml>`_,
                                (`diff <https://github.com/maykinmedia/open-product/compare/1.4.0..1.5.0>`_)
1.3.0           2025-10-13      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.4.0/src/producten-openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.4.0/src/producten-openapi.yaml>`_,
                                (`diff <https://github.com/maykinmedia/open-product/compare/1.2.0..1.4.0>`_)
1.2.0           2025-06-04      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.2.0/src/producten-openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.2.0/src/producten-openapi.yaml>`_,
                                (`diff <https://github.com/maykinmedia/open-product/compare/1.1.0..1.2.0>`_)
1.1.0           2025-05-09      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.1.0/src/producten-openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.1.0/src/producten-openapi.yaml>`_,
                                (`diff <https://github.com/maykinmedia/open-product/compare/1.0.0..1.1.0>`_)
1.0.0           2025-04-08      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.0.0/src/producten-openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.0.0/src/producten-openapi.yaml>`_
==============  ==============  =============================

Product types
-------------

==============  ==============  =============================
API version     Release date    API specification
==============  ==============  =============================
latest          n/a             `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-product/master/src/producttypen-openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-product/master/src/producttypen-openapi.yaml>`_,
                                (`diff <https://github.com/maykinmedia/open-product/compare/1.5.0..master>`_)
1.4.0           2025-12-04      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.5.0/src/producttypen-openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.5.0/src/producttypen-openapi.yaml>`_,
                                (`diff <https://github.com/maykinmedia/open-product/compare/1.4.0..1.5.0>`_)
1.3.0           2025-10-13      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.4.0/src/producttypen-openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.4.0/src/producttypen-openapi.yaml>`_,
                                (`diff <https://github.com/maykinmedia/open-product/compare/1.2.0..1.4.0>`_)
1.2.0           2025-06-04      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.2.0/src/producttypen-openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.2.0/src/producttypen-openapi.yaml>`_,
                                (`diff <https://github.com/maykinmedia/open-product/compare/1.1.0..1.2.0>`_)
1.1.0           2025-05-09      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.1.0/src/producttypen-openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.1.0/src/producttypen-openapi.yaml>`_,
                                (`diff <https://github.com/maykinmedia/open-product/compare/1.0.0..1.1.0>`_)
1.0.0           2025-04-08      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.0.0/src/producttypen-openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.0.0/src/producttypen-openapi.yaml>`_
==============  ==============  =============================

There a two ways to connect to authenticate with the API:

* An api token can be created in the Open Product admin -> Users -> Tokens.
* OpenId Connect can be configured in the Open Product admin -> Config -> OpenID connect configuration.



See: `All versions and changes <https://github.com/maykinmedia/open-product/blob/master/CHANGELOG.rst>`_


Developers
==========

|build-status| |coverage| |ruff| |python-versions|

This repository contains the source code for Open Product. To quickly
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

      $ wget https://raw.githubusercontent.com/maykinmedia/open-product/master/docker-compose.yml
      $ docker-compose up -d --no-build
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

.. |build-status| image:: https://github.com/maykinmedia/open-product/actions/workflows/ci.yml/badge.svg?branch=master
    :alt: Build status
    :target: https://github.com/maykinmedia/open-product/actions?query=workflow%3Aci

.. |coverage| image:: https://codecov.io/github/maykinmedia/open-product/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage
    :target: https://codecov.io/gh/maykinmedia/open-product

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Ruff

.. |python-versions| image:: https://img.shields.io/badge/python-3.12%2B-blue.svg
    :alt: Supported Python version

