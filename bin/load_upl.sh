#!/bin/bash

# load the current Uniforme Productnamen Lijst into Open Product
# Run this script from the root of the repository

set -e

if [[ "${LOAD_UPL,,}" =~ ^(true|1|yes)$ ]]; then
    # Figure out abspath of this script
    SCRIPT=$(readlink -f "$0")
    SCRIPTPATH=$(dirname "$SCRIPT")
    # wait for required services
    ${SCRIPTPATH}/wait_for_db.sh

    src/manage.py migrate
    src/manage.py load_upl --url https://standaarden.overheid.nl/owms/oquery/UPL-actueel.csv
fi
