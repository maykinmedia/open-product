#!/bin/bash
exec celery --workdir src --app openproduct flower
