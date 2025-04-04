# This is a multi-stage build file, which means a stage is used to build
# the backend (dependencies), the frontend stack and a final production
# stage re-using assets from the build stages. This keeps the final production
# image minimal in size.

# Stage 1 - Backend build environment
# includes compilers and build tooling to create the environment
FROM python:3.11-slim-bookworm AS backend-build

RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
        pkg-config \
        build-essential \
        # only relevant when using editable/github dependencies, which is discouraged
        # git \
        libpq-dev \
        shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN mkdir /app/src

# Ensure we use the latest version of pip
RUN pip install pip setuptools -U
COPY ./requirements /app/requirements
RUN pip install -r requirements/production.txt


# Stage 2 - Install frontend deps and build assets
FROM node:20-bookworm-slim AS frontend-build

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy configuration/build files
#COPY ./build /app/build/
COPY ./*.json ./*.js /app/
# ./.babelrc

# install WITH dev tooling
RUN npm ci

# copy source code
COPY ./src /app/src

# build frontend
RUN npm run build


# Stage 3 - Build docker image suitable for production
FROM python:3.11-slim-bookworm

# Stage 3.1 - Set up the needed production dependencies
# install all the dependencies for GeoDjango
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
        procps \
        nano \
        mime-support \
        postgresql-client \
        gettext \
        shared-mime-info \
        # lxml deps
        # libxslt \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ./bin/docker_start.sh /start.sh
COPY ./bin/celery_worker.sh /celery_worker.sh
COPY ./bin/celery_beat.sh /celery_beat.sh
COPY ./bin/celery_flower.sh /celery_flower.sh
RUN mkdir /app/bin /app/log /app/media /app/tmp

VOLUME ["/app/log", "/app/media"]

# copy backend build deps
COPY --from=backend-build /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=backend-build /usr/local/bin/uwsgi /usr/local/bin/uwsgi
COPY --from=backend-build /usr/local/bin/celery /usr/local/bin/celery
COPY --from=backend-build /app/src/ /app/src/

# copy frontend build statics
COPY --from=frontend-build /app/src/openproduct/static /app/src/openproduct/static

# copy source code
COPY ./src /app/src

RUN useradd -M -u 1000 maykin \
    && chown -R maykin:maykin /app

# drop privileges
USER maykin

ARG COMMIT_HASH RELEASE=latest
ENV RELEASE=${RELEASE} \
    GIT_SHA=${COMMIT_HASH} \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=openproduct.conf.docker

ARG SECRET_KEY=dummy

LABEL org.label-schema.vcs-ref=$COMMIT_HASH \
      org.label-schema.vcs-url="https://github.com/maykinmedia/open-product" \
      org.label-schema.version=$RELEASE \
      org.label-schema.name="open-product"

# Run collectstatic and compilemessages, so the result is already included in
# the image
RUN python src/manage.py collectstatic --noinput \
    && python src/manage.py compilemessages

EXPOSE 8000
CMD ["/start.sh"]
