Changelog
=========

1.6.0 (06-02-2026)
------------------

**New features**

    * [:open-product:`254`] Add eigenaar URN field to producttype
    * [:open-product:`253`] Add thema/subthema to Content Elements
    * [:open-product:`135`] Add direct_url to Actie

**Project maintance**

    * Upgrade dependencies

        * [:open-api-framework:`197`] ``commonground-api-common`` to 2.10.7
        * django to 5.2.11
        * protobuf to 6.33.4
        * cbor2 to 5.8.0
        * urllib3 to 2.6.3
        * mozilla-django-oidc-db to 1.1.1
        * notifications-api-common to 0.10.1
        * open-api-framework to 0.13.4
        * zgw-consumers to 1.2.0

    * Updated `uwsgi logs` from event to msg for high-cardinality log messages

**Bugfixes**

    * [:open-product:`260`] Fix API auth error when OIDC is not configured correctly
    * [:open-product:`266`] Fix wysimark so all Content Elements  are saved correctly
    * [:open-product:`239`] Fix help texts that do not have horizontal spacing in the admin
    * [:open-product:`271`] Fix missing toegestane_statussen is producttype admin
    * [:open-product:`271`] Disable notifications by default
    * Fix `celery logger` name

**Documentation**

    * [:open-api-framework:`197`] Fix documentation with maximum pagination ``page_size`` in the OAS.

1.5.0 (04-12-2025)
------------------

.. warning::

    Changes to format of ``setup_configuration`` data for OpenID connect

    In this release, ``mozilla-django-oidc-db`` has been updated to version 1.1.0, which requires the new data format.
    The old format is deprecated and will be removed in future releases.

    The new configuration must be used, as it splits the previous solo model configuration into ``OIDCProvider`` and ``OIDCClient``
    configurations, making it easier to re-use identity provider settings across multiple client IDs.

    Additionally, any configuration using ``django-setup-configuration`` must be updated to reflect these changes,
    as it is now split into two distinct sections: one for ``providers`` and one for ``clients``.
    This separation also exists in the admin interface, so both sections can be configured directly through the user interface.
    For example:

    .. code-block:: yaml

        providers:
          - identifier: example-provider
            # other provider settings
        clients:
          - identifier: admin-oidc
            oidc_provider_identifier: example-provider
            # other client settings

    For detailed configuration, see :ref:`Admin OIDC Configuration Step  <ref_step_mozilla_django_oidc_db.setup_configuration.steps.AdminOIDCConfigurationStep>`.
    Make sure to check which fields are marked as ``DEPRECATED`` and replace them with the fields that are mentioned as replacements.

**New features**

    * [:open-product:`230`] Add doelgroep to ProductType & make UPL requirement dependent on doelgroep
    * [:open-product:`228`] Add aanvullende_informatie to ContentElement
    * [:open-api-framework:`188`] Add csv option to data dump script (see :ref:`scripts` for more information)

    * [:open-api-framework:`152`] Add Open Telemetry support

    .. note::
        The OpenTelemetry SDK is **enabled by default**.
        If you do not have an endpoint to send system telemetry to, update your deployment to **disable it** by setting the environment variable:

        .. code-block:: bash

            OTEL_SDK_DISABLED=true

        If this is not done, warnings will be emitted to the container logs. The application will continue to function normally.
        All available metrics and details can be found in the :ref:`Observability documentation <installation_observability_index>`.

    * [:open-product:`237`] Replace ExterneVerwijzingConfig with urn/url fields.

        * Product Zaak, Taak, Document & ProductType ZaakType, VerzoekType & Proces now use urn/url fields. Mappings can be added in UrnMappingConfig.

    * [:open-product:`19`] Add ProductType object permissions to Producten API & admin.

        * (non super) Users now require read or read-write producttype object permissions to be able to create, update, read or delete product for a producttype
        * All models also now use class permissions for each crud operation.

**Project maintance**

    * Upgrade dependencies

        * [:open-api-framework:`171`] open-api-framework to 0.13.2
        * django to 5.2.8
        * [:open-api-framework:`191`] ``NodeJS`` to 24
        * [:open-api-framework:`176`] ``mozilla-django-oidc-db`` to 1.1.0
        * django-setup-configuration to 0.11.0
        * uwsgi to 2.0.31

    * [:open-api-workflows:`30`] Use API Design Rules linter for api spec validation
    * [:commonground-api-common:`134`] Ensure API errors are sent to Sentry
    * [:open-api-workflows:`31`] Update CI workflows

**Bugfixes**

    * [:open-product:`238`] Make Product prijs & frequentie optional

1.4.0 (13-10-2025)
------------------

.. warning::

     The default number of ``UWSGI_THREADS`` has been changed to 4.

**New features**

* [:open-product:`109`] added csv export for producttypes to admin and as management command
* [:open-api-framework:`157`] added datadump script
* [:open-product:`168`] added producttype `publicatie_start_datum` and `publicatie_eind_datum`
* added locatie & organisatie filters to product and producttype
* [:open-product:`201`] changed postcode validation to allow both with space and without and uppercase and lowercase, will be changed to correct format on save
* [:open-product:`187`] added required aanvraag zaak to product which can be saved as url or urn.
* improved exception handler with structlog see :ref:`manual_logging_exceptions`

**Bugfixes**

* [:open-product:`206`] fixed duplicate Elastic APM registration
* [:open-product:`195`] fixed content element response example in api spec
* [:open-product:`207`] fixed productstatechoices syntax warning
* [:open-product:`224`] fixed hoofd thema circular reference error

**Project maintenance**

* [:open-product:`212`] added issues to team bron project board
* [:open-api-framework:`85`] set default uwsgi threads to 4

* Upgrade dependencies

    * open-api-framework to 0.13.1
    * django to 5.2.7
    * zgw-consumers to 1.0.0
    * commonground-api-common to 2.10.0
    * django-setup-configuration to 0.9.0

1.3.0 (14-07-2025)
------------------

**New features**

* [:open-product:`164`] added product thema filters
* [:open-product:`172`] added read only uuid field to modeladmins
* [:open-product:`175`] added producttype naam filters
* [:open-product:`185`] changed producttype naam filters to nl only
* [:open-product:`170`] added `in aanvraag` status

**Bugfixes**

* [:open-product:`171`] changed product price to allow 0

**Project maintenance**

* [:open-product:`169`] added date automation to product status in api spec
* [:open-product:`152`] added structlog
* [:open-product:`176`] changed pagination keys to english
* [:open-api-framework:`148`] added postgres section to docs
* added prefetch & select related to viewsets
* added maykin-common

* Upgrade dependencies

  * open-api-framework to 0.11.0
  * urllib3 to 2.5.0
  * psycopg to 3.2.9
  * django-privates to 3.1.1

1.2.0 (13-06-2025)
------------------

.. warning::

    This release upgrades Django to version 5.2.3, which requires PostgreSQL version 14 or higher.
    Attempting to deploy with PostgreSQL <14 will cause errors during deployment.

**New features**

* [:open-product:`134`] added product taken & zaken
* [:open-product:`156`] changed contact to have a generic naam field
* [:open-api-framework:`149`] added dark/light theme toggle to the admin
* [:open-product:`131`] added product naam
* [:open-product:`119`] added thema filters

    * producttypen__uuid
    * producttypen__uuid__in

* [:open-product:`130`] added producttype code validation
* [:open-product:`123`] added dmn mapping and validation

**Bugfixes**

* fixed issue with UPL import
* [:open-product:`122`] fixed trailing slash api paths

**Project maintenance**

* Upgrade dependencies

  * django to 5.2.3
  * open-api-framework to 0.10.2
  * notifications-api-common to 0.7.3
  * commonground-api-common to 2.6.4
  * django-celery-beat to 2.8.0
  * tornado to 6.5.1
  * requests to 2.23.4

* added the quickstart workflow
* added image to web-init container in compose example
* [:open-api-framework:`139`] added django-upgrade-check
* [:open-api-framework:`140`] upgraded python to 3.12
* Replace OAS workflows with single workflow
* [:open-api-framework:`133`] Replace black, isort and flake8 with ``ruff`` and update ``code-quality`` workflow
* [:open-api-framework:`132`] Removed pytest & sphinx check

* [:open-product:`137`] follow api design rules

    * changed pagination keys to NL
    * moved openapi schemas
    * added API-Version header

**Documentation**

* [:open-product:`114`] added context to api specs
* [:open-product:`137`] added documentation about api design rules see :ref:`api_index`

1.1.0 (09-05-2025)
------------------

**New features**

* [:open-product:`104`] Added filters

    * ProductType themas__naam__in
    * ProductType themas__uuid__in
    * Product productype__naam__in
    * Product eigenaren__bsn
    * Product eigenaren__kvk_nummer
    * Product eigenaren__vestigingsnummer
    * Product eigenaren__klantnummer

**Project maintenance**

* [:open-product:`20`] Added support for django-setup-configuration. see :ref:`installation_configuration_cli`

* [:open-product:`100`] Added demodata fixture
* [:open-product:`88`] Updated CI workflows
* [:open-product:`116`] Fixed parler admin issues
* [:open-product:`106`] Fixed localemiddleware to only be active for the API
* Fixed readme links
* Fixed csp errors

**Documentation**

* [:open-product:`77`] Added datamodel diagrams
* [:open-product:`77`] Updated information model diagram

1.0.0 (08-04-2025)
------------------

**New features**

* [:open-product:`81`] Added product documenten verwijzing.
* [:open-product:`9`] Added Audit logging & reversion to all models.
* [:open-product:`15`] Added producttypen externe verwijzingen.
* [:open-product:`50`] Added oidc authentication to api.
* [:open-product:`66`] Added json filters for product dataobject & verbruiksobject.
* [:open-product:`14`] Added prijsregels & productype acties.
* [:open-product:`46`] Added product eigenaar.
* [:open-product:`43`] Added filters to all viewsets.
* [:open-product:`26`] Added producttype dataobject_schema & product dataobject.

**Bugfixes**

* [:open-product:`85`] Fixed product admin error.
* [:open-product:`95`] Fixed translation viewset issue.

**Project maintenance**

* [:open-product:`98`] Updated landing page and admin styling.
* [:open-product:`9`] Removed sites.
* [:open-product:`48`] Renamed product_type to producttype.
* [:open-product:`78`] Renamed project to open product.
* [:open-product:`76`] Updated api docs.
* [:open-product:`89`] Fixed docker compose example.
* [:open-product:`70`] Recreated migrations.



0.0.5 (11-03-2025)
------------------

**New features**

* [:open-product:`52`] Added interne opmerkingen field to producttype.
* [:open-product:`13`] Added externe codes to producttype.
* [:open-product:`12`] Added parameters to producttype.
* [:open-product:`18`] Added integration with Open Notificaties.
* [:open-product:`31`] Added producttype verbruiksobject_schema & product verbruiksobject.



0.0.4 (18-02-2025)
------------------

**Project maintenance**

* [:open-product:`29`] added docs github action job

**Documentation**

* [:open-product:`29`] Added Read the Docs documentation
* [:open-product:`29`] Added CHANGELOG file

**New features**

* Added multi-language support for PRODUCTTYPEN.
* Added CONTENTELEMENTEN & CONTENTLABELS.


0.0.3 (04-02-2025)
------------------

**New features**

* Added Celery to the project
* Added ``code`` field to *ORGANISATIES*
* Added audit logging for several resources
* Added ``status``, ``prijs`` and ``frequentie`` fields to *PRODUCTEN*
* Added ``code`` and ``toegestaneStasussen`` fields to *PRODUCTTYPES*

**Breaking changes**

* Added admin validation for *PRODUCTEN*


0.0.2 (17-01-2025)
------------------

**Breaking changes**

* Moved from rest framework's pagination
* Moved default database from postgis to postgres

**New features**

* Added endpoints for *LOCATIES*
* Added endpoints for *PRODUCTEN*
* Added frontend related pages (e.g homepage, open api spec linking pages)

**Documentation**

* Splitted openapi spec into two seperate files, one for *PRODUCTTYPES* and one for *PRODUCTS*


0.0.1 (02-01-2025)
------------------

🎉 First release of Open Product.

Features:

* Producttype API
* Vragen API
* Prijzen API
* Themas API
* Links API
* Bestanden API
* Automated test suite
