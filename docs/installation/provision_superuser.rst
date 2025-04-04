.. _installation_provision_superuser:

Provisioning a superuser
========================

A clean installation of Open Prodcuten has no existing data, it's up to the service provider
and/or the users to set up Open Product to your liking.

To be able to do anything in the Open Product admin interface, you need a user account
with sufficient permissions, typically a superuser. Open Product has a couple of mechanisms
to create this superuser.

Creating a superuser manually
-----------------------------

Superusers can be created through the :ref:`installation_reference_cli` built into Open
Producten, for example:

.. code-block:: bash

    python src/manage.py createinitialsuperuser \
        --username admin \
        --password admin \
        --email admin@gemeente.nl \
        --no-input

This will create the user if it does not exist yet. If the user already exists (based
on username), nothing happens.

You can get detailed information by getting the built-in help:

.. code-block:: bash

    python src/manage.py createinitialsuperuser --help
