#!/bin/sh
#
# Generate the API schema from the code into the output file.
#
# Run this script from the root of the repository:
#
#   ./bin/generate_api_schema.sh
#

src/manage.py spectacular \
    --validate \
    --fail-on-warn \
    --lang=nl \
    --urlconf openproduct.producttypen.urls \
    --file src/producttypen-openapi.yaml

src/manage.py spectacular \
    --validate \
    --fail-on-warn \
    --lang=nl \
    --urlconf openproduct.producten.urls \
    --file src/producten-openapi.yaml

