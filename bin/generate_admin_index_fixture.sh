#!/bin/bash

#

# Dump the current (local database) admin layout to a JSON fixture. This

# overwrites the existing one.

#

# You can load this fixture with:

# $ src/manage.py loaddata default_admin_index

#

# Run this script from the root of the repository

mkdir -p src/openproduct/fixtures

src/manage.py dumpdata --indent=4 --natural-foreign --natural-primary admin_index.AppGroup admin_index.AppLink > src/openproduct/fixtures/default_admin_index.json
