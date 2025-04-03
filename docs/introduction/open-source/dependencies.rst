.. _introduction_open-source_deps:

Open Source dependencies
========================

Open Product would not be possible without a number of other Open Source dependencies.

Most notably, the backend is written in the Python_ programming language. We use the
Django_ framework to build the web-application (which includes the API of course) that
is Open Product.

The core elements for the API implementation are:

* `Django REST framework`_ (DRF), to implement the RESTful API
* `drf-spectacular`_ to generate the API documentation in the form of OAS 3.0 specification
* `VNG-API-common`_, a re-usable library with some specific VNG/Dutch API tooling, built
  on top of DRF and drf-spectacular

.. _Python: https://www.python.org/
.. _Django: https://www.djangoproject.com/
.. _Django REST framework: https://www.django-rest-framework.org/
.. _VNG-API-common: https://commonground-api-common.readthedocs.io/en/latest/
.. _drf-spectacular: https://drf-spectacular.readthedocs.io/en/latest/

What about the dependencies that don't have a 1.0.0 version (yet)?
------------------------------------------------------------------

Good question!

Most libraries follow semantic versioning, which takes the form of ``A.B.c`` version
numbering. In this pattern, ``A`` is the major version, ``B`` is the minor version and
``c`` is the patch version. Roughly speaking, if ``A`` increments, you can expect
breaking changes. If ``B`` increments, the changes are backwards compatible fixes and
new features, and if ``c`` changes, it's purely a bugfix release.

Libraries with a version like ``0.x.y`` are usually considering not-stable yet - as long
as no ``1.0.0`` release has happened, the internal API can change, or the project may
never reach that "maturity" you'd want.

If you look at our requirements_, you will see a couple of libraries that don't have a
1.0.0 version (yet). So, why do we depend on them, and is there a risk of depending on
them? Below, you can find the mitigations/reasoning why we decided to depend on them
anyway, in alphabetical order.

* ``coreschema==0.0.4`` is a transitive dependency of ``coreapi`` and ``drf-yasg``,
  which are both well-maintained. It is made by the same author as DRF itself.

* ``drf-nested-routers==0.94.1`` sees regular maintenance and activity on Github, with
  high popularity.

* ``inflection==0.5.1`` transitive dependency of drf-spectacular, which is quite a popular
  project.

* ``iso-639==0.4.5`` stable package that just happens to never have been named 1.0.
  ISO-639 is an international standard, which don't tend to change.

* ``isodate==0.7.2`` yet another library to parse ISO-8601 dates. Transitive dependency
  of ``vng-api-common``.

* ``sqlparse==0.5.2`` direct dependency of Django. Given the widespread use of Django,
  this should not pose any problems.

* ``zgw-consumers==0.35.1`` library maintained by Maykin Media.

.. _`requirements`: https://github.com/maykinmedia/open-product/blob/master/requirements/base.txt
