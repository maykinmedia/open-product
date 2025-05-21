.. _development_principles:

Principles and code style (draft)
=================================

Defining (architectural) principles and code style keeps the code base consistent
and manages expectations for contributions.

Backend
-------

On the backend, we use the `Django framework`_ and follow the project structure
of having apps within the project.

- Django apps contains models, views and API definitions. They group a logical part of
  the greater project which is loosely coupled to other apps.

  Tests are in the django app package. Split tests in logical modules, and try to avoid
  complex nesting structures.

- All apps must go in the ``src/openproduct`` directory, which namespaces all the Open Product
  code in the ``openproduct`` package. This prevents name conflicts with third party
  applications.

- Application names should always be in plural form.

- Settings go in ``openproduct.conf``, which is split according to deploy environment:

      - dev
      - ci
      - staging
      - production
      - docker

  Settings must always be defined in the ``openproduct.conf.base`` with sane defaults.

- Global runtime Open Product configuration (database backed) should go in the
  ``openproduct.config`` app.

- Generic tools that are used by specific apps should be a ``openproduct`` sub-package,
  or possibly go in ``openproduct.utils``.

- Integration with other, third-party services/interfaces should go in a
  ``openproduct.contrib`` package. This is currently (!) not the case yet.

- Code style and imports are enforced in CI with `ruff`_.

.. _Django framework: https://www.djangoproject.com/
.. _ruff: https://github.com/astral-sh/ruff