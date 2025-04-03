
Release process
===============

Open Product makes use of quite a bit of Continuous Integration tooling to
set up a full release process, all driven by the Git repository.

Github Actions
--------------

Our pipeline is mostly implemented on Github Actions:

Merges to the ``master`` branch are built on Github, where:

1. Tests are run
2. Code quality checks are run
3. Automated tests are run
4. The Docker image is built and published

..
    TODO: uncomment this when this is setup
    If the build is for a Git tag on the ``master`` branch, then the image is
    built and publish with that version tag to Docker Hub.

Releasing a new version
-----------------------

Releasing a new version can only be done by people with merge permissions to
the ``master`` branch belonging to the `Maykin`_ organisation on Github.

Assuming a current version of ``0.9.0``:

**Create a release branch**

.. code-block:: bash

    git checkout -b release/1.0.0

**Update the changelog**

Update ``CHANGELOG.rst`` in the root of the project, and make sure to commit the
changes.

**Editing files**

Various files will contain the current version number. These files will have to
be adjusted where applicable.

and commit:

.. code-block:: bash

    git commit -am ":bookmark: Bump version to 1.0.0"

Push the changes and make a pull request.

**Tag the release**

Once the PR is merged to main, check out the ``master`` branch and tag it:

.. code-block:: bash

    git checkout main
    git pull
    git tag 1.0.0

Tagging will ensure that a Docker image ``maykinmedia/open-product:1.0.0`` is published.

. _`Maykin`: https://github.com/maykinmedia
