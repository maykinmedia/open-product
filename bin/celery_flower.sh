#!/bin/bash

# Set defaults for OTEL
export OTEL_SERVICE_NAME="${OTEL_SERVICE_NAME:-openproduct-flower}"

exec celery --workdir src --app openproduct flower
