#!/usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

docker-compose -f "$DIR/docker-compose.yaml" -p reportcard \
  exec reportcard python -m reportcard "$@"