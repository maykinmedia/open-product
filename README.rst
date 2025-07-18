============
Open Product
============

:Version: 1.3.0
:Source: https://github.com/maykinmedia/open-product
:Keywords: ``producten``

Plek voor gemeenten om producttypen en producten te beheren om ze te gebruiken in andere applicaties.
(`English version`_)

Ontwikkeld door `Maykin B.V.`_.


Introductie
===========

Open Product is een applicatie waarin producttypen en producten op een enkele plek kunnen worden beheerd.
Andere applicaties zoals Open Inwoner en Open Formulieren kunnen met Open Product via een REST API integreren om bijvoorbeeld producttypen informatie te tonen, producten aan te maken of om de actuele prijs van een producttype op te halen.

In Open Product worden producttypen en producten opgeslagen. Een producttype is bijvoorbeeld een parkeervergunning en bevat alle relevante informatie zoals wat de regels zijn, hoe verschillende zones werken enz.
Een product is in dit voorbeeld een parkeervergunning van een persoon en bevat in dit geval het kenteken en de persoonsgegevens.

Informatiemodel
===============

.. image:: docs/introduction/assets/open-product-informatiemodel-diagram.png
   :alt: Open Product informatiemodel



API specificatie
================

Producten
---------

==============  ==============  =============================
Versie          Release datum   API specificatie
==============  ==============  =============================
latest          n/a             `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-product/master/src/producten-openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-product/master/src/producten-openapi.yaml>`_,
                                (`diff <https://github.com/maykinmedia/open-product/compare/1.2.0..master>`_)
1.2.0           2025-06-04      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.2.0/src/producten-openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.2.0/src/producten-openapi.yaml>`_,
                                (`diff <https://github.com/maykinmedia/open-product/compare/1.1.0..1.2.0>`_)
1.1.0           2025-05-09      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.1.0/src/producten-openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.1.0/src/producten-openapi.yaml>`_,
                                (`diff <https://github.com/maykinmedia/open-product/compare/1.0.0..1.1.0>`_)
1.0.0           2025-04-08      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.0.0/src/producten-openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.0.0/src/producten-openapi.yaml>`_
==============  ==============  =============================

Producttypen
------------

==============  ==============  =============================
Versie          Release datum   API specificatie
==============  ==============  =============================
latest          n/a             `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-product/master/src/producttypen-openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-product/master/src/producttypen-openapi.yaml>`_,
                                (`diff <https://github.com/maykinmedia/open-product/compare/1.2.0..master>`_)
1.2.0           2025-06-04      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.2.0/src/producttypen-openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.2.0/src/producttypen-openapi.yaml>`_,
                                (`diff <https://github.com/maykinmedia/open-product/compare/1.1.0..1.2.0>`_)
1.1.0           2025-05-09      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.1.0/src/producttypen-openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.1.0/src/producttypen-openapi.yaml>`_,
                                (`diff <https://github.com/maykinmedia/open-product/compare/1.0.0..1.1.0>`_)
1.0.0           2025-04-08      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.0.0/src/producttypen-openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-product/1.0.0/src/producttypen-openapi.yaml>`_
==============  ==============  =============================

Er zijn twee manieren om te authenticeren met de API.

* Een api token kan worden aangemaakt in Open Product admin -> Users -> Tokens.
* OpenId Connect kan worden ingesteld in the Open Product admin -> Configuratie -> OpenID connect configuratie.


See: `Alle versies en veranderingen <https://github.com/maykinmedia/open-product/blob/master/CHANGELOG.rst>`_


Ontwikkelaars
=============

|build-status| |coverage| |ruff| |python-versions|

Deze repository bevat de broncode voor Open Product. Om snel aan de slag
te gaan, raden we aan om de Docker image te gebruiken. Uiteraard kan je ook
het project zelf bouwen van de broncode. Zie hiervoor
`INSTALL.rst <INSTALL.rst>`_.

Open Product bestaat uit drie apps:

* producttypen
* producten
* locaties (& organisaties)

Quickstart
----------

1. Download en start openproduct:

   .. code:: bash

      $ wget https://raw.githubusercontent.com/maykinmedia/open-product/master/docker-compose.yml
      $ docker-compose up -d --no-build
      $ docker compose exec -T web src/manage.py loaddata demodata
      $ docker-compose exec web src/manage.py createsuperuser

2. In de browser, navigeer naar ``http://localhost:8000/`` om de beheerinterface
   en de API te benaderen.


Links
=====

* `Documentatie <https://open-product.readthedocs.io/en/stable/>`_
* `Docker image <https://hub.docker.com/r/maykinmedia/open-product>`_
* `Issues <https://github.com/maykinmedia/open-product/issues>`_
* `Code <https://github.com/maykinmedia/open-product>`_


Licentie
========

Copyright © Maykin 2024

Licensed under the EUPL_


.. _`English version`: README.EN.rst

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

