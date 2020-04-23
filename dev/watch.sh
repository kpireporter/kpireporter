#!/usr/bin/env bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

_dockercompose() {
  docker-compose -f "$DIR/docker-compose.yaml" -p reportcard "$@"
}

echo "Removing existing containers ..."
_dockercompose down

echo "Rebuilding application container ..."
_dockercompose build -q reportcard
_dockercompose rm -f --stop reportcard

echo "Regenerating fixture data ..."
pushd "$DIR" >/dev/null; python -m "datasources"; popd >/dev/null

echo "Starting docker-compose stack ..."
_dockercompose up --quiet-pull --force-recreate -d

for bin in ag entr; do
  if ! type -f "$bin" >/dev/null 2>&1; then
    echo "ERROR: You must install the '$bin' tool to take advantage of the"
    echo "watch functionality."
    exit 1
  fi
done

echo
echo "Starting watcher ..."
echo

ag -l -G 'examples|reportcard' . "$DIR/.." | entr "$DIR/run.sh" "$@"
