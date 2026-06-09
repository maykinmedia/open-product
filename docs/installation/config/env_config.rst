.. _installation_env_config:

===================================
Environment configuration reference
===================================


The Open Product API can be run both as a Docker container or a VPS / dedicated server.
It relies on other services, such as database and cache backends, which can be configured through environment variables.


Available environment variables
===============================

.. config-all-params::

Urns
----

* ``REQUIRE_URN_URL_MAPPING``: whether an urn requires an url mapping. Defaults to: ``True``.
* ``REQUIRE_URL_URN_MAPPING``: whether an url requires an urn mapping. Defaults to: ``False``.


Initial superuser creation (Docker only)
----------------------------------------

A clean installation of Objects API comes without pre-installed or pre-configured admin
user by default.

Users of Objects API can opt-in to provision an initial superuser via environment
variables. The user will only be created if it doesn't exist yet.

* ``OPENPRODUCT_SUPERUSER_USERNAME``: specify the username of the superuser to create. Setting
  this to a non-empty value will enable the creation of the superuser. Default empty.
* ``OPENPRODUCT_SUPERUSER_EMAIL``: specify the e-mail address to configure for the superuser.
  Defaults to `admin@admin.org`. Only has an effect if ``OPENPRODUCT_SUPERUSER_USERNAME`` is set.
* ``OPENPRODUCT_SUPERUSER_PASSWORD``: specify the password for the superuser. Default empty,
  which means the superuser will be created _without_ password. Only has an effect
  if ``OPENPRODUCT_SUPERUSER_USERNAME`` is set.

Initial configuration
---------------------

Both Objects API and Objecttypes API support `setup_configuration` management command,
which allows configuration via environment variables.
All these environment variables are described at :ref:`command line <installation_configuration_cli>`.



Specifying the environment variables
=====================================

There are two strategies to specify the environment variables:

* provide them in a ``.env`` file
* start the component processes (with uwsgi/gunicorn/celery) in a process
  manager that defines the environment variables

Providing a .env file
---------------------

This is the most simple setup and easiest to debug. The ``.env`` file must be
at the root of the project - i.e. on the same level as the ``src`` directory (
NOT *in* the ``src`` directory).

The syntax is key-value:

.. code::

   SOME_VAR=some_value
   OTHER_VAR="quoted_value"


Provide the envvars via the process manager
-------------------------------------------

If you use a process manager (such as supervisor/systemd), use their techniques
to define the envvars. The component will pick them up out of the box.
