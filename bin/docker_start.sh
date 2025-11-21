#!/bin/sh

set -ex

# Wait for the database container
# See: https://docs.docker.com/compose/startup-order/
export PGHOST=${DB_HOST:-db}
export PGPORT=${DB_PORT:-5432}

uwsgi_port=${UWSGI_PORT:-8000}
uwsgi_processes=${UWSGI_PROCESSES:-4}
uwsgi_threads=${UWSGI_THREADS:-4}

mountpoint=${SUBPATH:-/}

# wait for required services
${SCRIPTPATH}/wait_for_db.sh

>&2 echo "Database is up."

# Set defaults for OTEL
export OTEL_SERVICE_NAME="${OTEL_SERVICE_NAME:-openproduct}"

# Apply database migrations
>&2 echo "Apply database migrations"
OTEL_SDK_DISABLED=True python src/manage.py migrate

# Create superuser
# specify password by setting OPENPRODUCT_SUPERUSER_PASSWORD in the env
# specify username by setting OPENPRODUCT_SUPERUSER_USERNAME in the env
# specify email by setting OPENPRODUCT_SUPERUSER_EMAIL in the env
if [ -n "${OPENPRODUCT_SUPERUSER_USERNAME}" ]; then
    python src/manage.py createinitialsuperuser \
        --no-input \
        --username "${OPENPRODUCT_SUPERUSER_USERNAME}" \
        --email "${OPENPRODUCT_SUPERUSER_EMAIL:-admin@admin.org}"
    unset OPENPRODUCT_SUPERUSER_USERNAME OPENPRODUCT_SUPERUSER_EMAIL OPENPRODUCT_SUPERUSER_PASSWORD
fi

# Start server
>&2 echo "Starting server"
exec uwsgi \
    --ini "${SCRIPTPATH}/uwsgi.ini" \
    --http :$uwsgi_port \
    --http-keepalive \
    --manage-script-name \
    --mount $mountpoint=openproduct.wsgi:application \
    --static-map /static=/app/static \
    --static-map /media=/app/media  \
    --chdir src \
    --enable-threads \
    --processes $uwsgi_processes \
    --threads $uwsgi_threads \
    --post-buffering=8192 \
    --buffer-size=65535
    # processes & threads are needed for concurrency without nginx sitting inbetween
