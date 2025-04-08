
1.0.0 (08-04-2025)
------------------

**New features**

* [#81] Added product documenten verwijzing.
* [#9] Added Audit logging & reversion to all models.
* [#15] Added producttypen externe verwijzingen.
* [#50] Added oidc authentication to api.
* [#66] Added json filters for product dataobject & verbruiksobject.
* [#14] Added prijsregels & productype acties.
* [#46] Added product eigenaar.
* [#43] Added filters to all viewsets.
* [#26] Added producttype dataobject_schema & product dataobject.

**Bugfixes**

* [#85] Fixed product admin error.
* [#95] Fixed translation viewset issue.

**Project maintenance**

* [#98] Updated landing page and admin styling.
* [#9] Removed sites.
* [#48] Renamed product_type to producttype.
* [#78] Renamed project to open product.
* [#76] Updated api docs.
* [#89] Fixed docker compose example.
* [#70] Recreated migrations.



0.0.5 (11-03-2025)
------------------

**New features**

* [#52] Added interne opmerkingen field to producttype.
* [#13] Added externe codes to producttype.
* [#12] Added parameters to producttype.
* [#18] Added integration with Open Notificaties.
* [#31] Added producttype verbruiksobject_schema & product verbruiksobject.



0.0.4 (18-02-2025)
------------------

**Project maintenance**

* [#29] added docs github action job

**Documentation**

* [#29] Added Read the Docs documentation
* [#29] Added CHANGELOG file

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
