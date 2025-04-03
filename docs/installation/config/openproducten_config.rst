.. _installation_configuration:

====================================
Open Producten configuration (admin)
====================================

Before you can work with Open Producten after installation, a few settings need to be
configured first.

.. note::

    This document describes the manual configuration via the admin.

.. _installation_configuration_sites:

Setting the domain
==================

In the admin, under **Configuratie > Websites**, make sure to change the existing
``Site`` to the domain under which Open Producten will be deployed (see
:ref:`the manual<manual_configuration>` for more information).

.. note:: Due to a cache-bug in the underlying framework, you need to restart all
   replicas for this change to take effect everywhere.

.. _installation_configuration_notificaties_api:

Configure Notificaties API
==========================

Next, the notifications for Open Producten must be configured. We assume you're also
using Open Notificaties to make a complete setup.

Open Producten
--------------

The configuration steps below need to be performed in Open Producten itself.

**Open Producten consuming the Notificaties API**

1. Configure the credentials for the Notificaties API (so Open Producten can access
   the Notificaties API):

   a. Navigate to **API Autorisaties > Services**
   b. Select Click **Service toevoegen** (or select the notifications service if
      it already exists).
   c. Fill out the form:

      - **Label**: *For example:* ``Open Notificaties``
      - **Service slug**: *For example:* ``open-notificaties``
      - **Type**: Select the option: ``NRC (Notifications)``
      - **API root url**: the full URL to the Notificaties API root, e.g.
        ``https://notificaties.gemeente.local/api/v1/``

      - **Client ID**: An existing Client ID for the notifications service, or create
        one and configure the same value in Open Notificaties - *For example:* ``open-producten``
      - **Secret**: *Some random string. You will need this later on!*
      - **Authorization type**: Select the option: ``ZGW client_id + secret``
      - **OAS url**: URL that points to the OpenAPI specification. This is typically
        ``<API-ROOT>/schema/openapi.yaml``, *for example:*
        ``https://notificaties.gemeente.local/api/v1/schema/openapi.yaml``
      - **User ID**: *Same as the Client ID*
      - **User representation**: *For example:* ``Open Producten``

   d. Click **Opslaan**.

2. Next, configure Open Producten to use this service for the Notificaties API:

   a. Navigate to **Configuratie > Notificatiescomponentconfiguratie**
   b. Select the service from the previous step in the **Notifications api service**
      dropdown.
   c. Sending notifications support autoretry mechanism, which can be also configured here.
      Fill out the following properties:

      - **Notification delivery max retries**: the maximum number of retries the task queue
        will do if sending a notification failed. Default is ``5``.
      - **Notification delivery retry backoff**: a boolean or a number. If this option is set to
        ``True``, autoretries will be delayed following the rules of exponential backoff. If
        this option is set to a number, it is used as a delay factor. Default is ``3``.
      - **Notification delivery retry backoff max**: an integer, specifying number of seconds.
        If ``Notification delivery retry backoff`` is enabled, this option will set a maximum
        delay in seconds between task autoretries. Default is ``48`` seconds.
   d. Click **Opslaan**.


Register notification channels
==============================

Open Producten
--------------

Before notifications can be sent to ``kanalen`` in Open Notificaties, these ``kanalen``
must first be registered via Open Producten.

Register the required channels:

.. code-block:: bash

    python src/manage.py register_kanalen

Create an API token
===================

Open Producten
--------------
By creating an API token, we can perform an API test call to verify the successful
installation.

Navigate to **Users** > **Token** and click on **Token toevoegen**
in the top right.

1. Select the user you want to create a token for
2. Click **Opslaan** in the bottom left

After creating the **Token** the **key** is shown in the list page. This value
can be used in the ``Authorization`` header.


Making an API call
------------------

We can now make an HTTP request to one of the APIs of Open Producten. For this
example, we have used `curl`_ to make the request.

.. code-block:: bash

   curl --request GET \
   --header 'Authorization: Token 1d4df96cfe14543558118805c5e9252629e805a0' \
   --header 'Content-Type: application/json' \
   {{base_url}}/producten/api/v1/producten

The example above uses the same value configured in
:ref:`installation_configuration_sites`.

.. _Curl: https://curl.se/docs/manpage.html

Configure openID connect
========================

Open Producten
--------------

Navigate to **Config** > **OpenID**.

1. Fill in the fields required for the provider you want to use. See :ref:`manual_oidc`.
2. Enable the configuration.
3. Click **Opslaan** in the bottom left

After creating the **Token** the **key** is shown in the list page. This value
can be used in the ``Authorization`` header.


Making an API call
------------------

We can now make an HTTP request to one of the APIs of Open Producten. For this
example, we have used `curl`_ to make the request.

.. code-block:: bash

   curl --request GET \
   --header 'Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cC.....' \
   --header 'Content-Type: application/json' \
   {{base_url}}/producten/api/v1/producten

The example above uses the same value configured in
:ref:`installation_configuration_sites`.

.. _Curl: https://curl.se/docs/manpage.html
