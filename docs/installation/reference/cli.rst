.. _installation_reference_cli:

Command Line Interface (CLI)
============================

Open Product ships with a command line interface accessible inside of the containers.

To get more information about a command, you can run:

.. code-block:: bash

    $ python src/manage.py <command> --help

Available commands
------------------

``createinitialsuperuser``
    Creates an initial superuser with the specified username and e-mail address.

    The password can be provided upfront with the ``--password`` CLI argument, or by
    using the ``DJANGO_SUPERUSER_PASSWORD`` environment variable. Additionally,
    with ``--generate-password`` a password can be generated and e-mailed to the
    specified e-mail address. Note that this requires your e-mail configuration to be
    set up correctly (any of the ``EMAIL_*`` envvars)!

``load_upl``
    Loads ``Uniforme product naam``'s (UPN) from the given filepath or URL.

    Either the ``--file`` or the ``--url`` option should be used when this command is ran.
    Both of the arguments expect to point to a CSV file with appropriate columns.
    The ``is_verwijderd`` value will be set to ``True`` for existing (which were
    present before the command was ran) UPN's.
