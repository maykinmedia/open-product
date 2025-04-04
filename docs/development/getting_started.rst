.. _development_getting_started:

===============
Getting started
===============

The project is developed in Python using the `Django framework`_. There are 3
sections below, focussing on developers, running the project using Docker and
hints for running the project in production.

.. _Django framework: https://www.djangoproject.com/

Installation
============

Prerequisites
-------------

You need the following libraries and/or programs:

* `Python`_ 3.11
* Python `Virtualenv`_ and `Pip`_
* `PostgreSQL`_ 15.0 or above
* `Docker`_ 19.03 or above (and `docker-compose`_)

.. _Python: https://www.python.org/
.. _Virtualenv: https://virtualenv.pypa.io/en/stable/
.. _Pip: https://packaging.python.org/tutorials/installing-packages/#ensure-pip-setuptools-and-wheel-are-up-to-date
.. _PostgreSQL: https://www.postgresql.org
.. _Docker: https://www.docker.com/
.. _docker-compose: https://docs.docker.com/compose/install/


Step by step
------------

Developers can follow the following steps to set up the project on their local
development machine.

1. Navigate to the location where you want to place your project.

2. Get the code:

   .. code-block:: bash

       $ git clone git@github.com:maykinmedia/open-product.git
       $ cd open-product

3. At this point you can already built the Docker image and run Open Product.
   You can skip this if you don't want that.

   .. code-block:: bash

       $ docker-compose up

   **Note:** If you are using Git on Windows, line-endings might change in
   checked out files depending on your `core.autocrlf` setting in `.gitconfig`.
   This is problematic because files are copied into a Docker image, which runs
   on Linux. Specifically, the `bin/docker_start.sh` file is affected by this
   which causes the Docker container fail to start up.

4. Install all required libraries:

   .. code-block:: bash

       $ virtualenv env  # or, python -m venv env
       $ source env/bin/activate
       $ pip install --requirement requirements/dev.txt

5. Activate your virtual environment and create the statics and database:

   .. code-block:: bash

       $ source env/bin/activate
       $ python src/manage.py migrate

6. Create a superuser to access the management interface:

   .. code-block:: bash

       $ python src/manage.py createsuperuser

7. You can now run your installation and point your browser to the address
   given by this command:

   .. code-block:: bash

       $ python src/manage.py runserver


**Note:** If you are making local, machine specific, changes, add them to
``src/openproduct/conf/local.py``. You can also set certain common
variables in a local ``.env`` file. You can base these files on the
example files included in the same directory.

Update installation
-------------------

When updating an existing installation:

1. Activate the virtual environment:

   .. code-block:: bash

       $ cd open-product
       $ source env/bin/activate

2. Update the code and libraries:

   .. code-block:: bash

       $ git pull
       $ pip install --requirement requirements/dev.txt

3. Update the statics and database:

   .. code-block:: bash

       $ python src/manage.py migrate


Testsuite
---------

To run the test suite:

.. code-block:: bash

    $ python src/manage.py test openproduct

Configuration via environment variables
---------------------------------------

A number of common settings/configurations can be modified by setting
environment variables, add them to your ``.env`` file or persist them in
``src/openproduct/conf/local.py``.

* ``SECRET_KEY``: the secret key to use. A default is set in ``dev.py``

* ``DB_NAME``: name of the database for the project. Defaults to ``openproduct``.
* ``DB_USER``: username to connect to the database with. Defaults to ``openproduct``.
* ``DB_PASSWORD``: password to use to connect to the database. Defaults to ``openproduct``.
* ``DB_HOST``: database host. Defaults to ``localhost``
* ``DB_PORT``: database port. Defaults to ``5432``.

* ``SENTRY_DSN``: the DSN of the project in Sentry. If set, enabled Sentry SDK as
  logger and will send errors/logging to Sentry. If unset, Sentry SDK will be
  disabled.


Settings
========

All settings for the project can be found in `src/openproduct/conf``.
The file ``local.py`` overwrites settings from the base configuration,
and is only loaded for the dev settings.

.. TODO: remove Celery part below? No references for usage found in project

Running background tasks
=====================================

We use `Celery`_ as background task queue.

You can run celery worker(s) in a shell to activate the asynchronous task
queue processing.

To start the background workers executing tasks:

.. code-block:: bash

   $ ./bin/celery_worker.sh


To start flower for task monitoring:

.. code-block:: bash

   $ ./bin/celery_flower.sh


.. _Celery: https://docs.celeryq.dev/en/stable/
