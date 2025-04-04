.. _installation_reference_containers:

Container configuration
=======================

Open Product is typically deployed as containers. There are some implementation details
relevant to properly configure this in your infrastructure.

Permissions
-----------

Open Product containers do not run as the root user, but instead drop privileges.


* Container user: ``maykin``, with ``UID: 1000``
* Container user group: ``maykin``, with ``GID: 1000``
