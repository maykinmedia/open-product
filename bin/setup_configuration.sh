#!/bin/bash

# setup initial configuration using environment variables
# Run this script from the root of the repository

set -e

if [[ "${RUN_SETUP_CONFIG,,}" =~ ^(true|1|yes)$ ]]; then
    # Figure out abspath of this script
    SCRIPT=$(readlink -f "$0")
    SCRIPTPATH=$(dirname "$SCRIPT")
    # wait for required services
    ${SCRIPTPATH}/wait_for_db.sh

    src/manage.py migrate
    src/manage.py setup_configuration --yaml-file setup_configuration/data.yaml
fi
