#!/usr/bin/env sh
set -e

docker-compose run test test "$@"
