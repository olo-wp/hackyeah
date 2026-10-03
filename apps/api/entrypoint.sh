#!/bin/sh
set -eu

: "${DATABASE_URL:?Set DATABASE_URL to your PostgreSQL connection URL}"

routeable-migrate
exec "$@"
