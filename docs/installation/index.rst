.. _installation_index:

Installation
============

You can install Open Product in several ways, depending on your intended purpose and
expertise.

.. TODO:

    1. Deploy on :ref:`Kubernetes <installation_kubernetes>` for public testing and
       production purposes
    2. Deploy on a :ref:`VM, VPS or dedicated server <installation_ansible>` with Docker
       Engine (or Podman) for public testing and production purposes
    3. Run with :ref:`docker compose <installation_docker_compose>` on your computer for
       private testing purposes
    4. Run from :ref:`Python code <development_getting_started>` on your computer for
       development purposes

Before you begin
----------------

.. note:: These requirements are aimed towards public testing and production
   deployments, though they are _interesting_ to understand the workings of Open Product.

.. TODO:
   * Check the :ref:`minimum system requirements<installation_hardware>` for the target
    machine(s).

* Ensure you have the :ref:`installation_prerequisites` available
* Make sure the target machine(s) have access to the Internet.
* The target machine(s) should be reachable via at least a local DNS entry:

  * Open Product: ``open-product.<organization.local>``
  * `Open Notificaties`_: ``open-notificaties.<organization.local>``

    .. note:: Notifications can be disabled using ``NOTIFICATIONS_DISABLED`` (see :ref:`installation_env_config`).


  The machine(s) do not need to be publicly accessible and do not need a public DNS
  entry. In some cases, you might want this but it's not recommended. The same machine
  can be used for both Open Product and `Open Notificaties`_.

.. _`Open Notificaties`: https://github.com/open-zaak/open-notificaties

Guides
------

.. toctree::
   :maxdepth: 1

   docker_compose
   provision_superuser
   config/index
   updating

Reference
---------

.. toctree::
   :maxdepth: 1

   reference/prerequisites
   reference/cli
   reference/logging
   reference/containers
   reference/time
