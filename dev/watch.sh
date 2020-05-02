#!/usr/bin/env bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

pushd "$DIR" >/dev/null

_dockercompose() {
  docker-compose -p reportcard "$@"
}

log() {
  echo "$@" >&2
}

log_step() {
  for i in {1..80}; do printf "*" >&2; done
  log
  log "$@"
  for i in {1..80}; do printf "*" >&2; done
  log
}

rebuild() {
  mkdir -p "$DIR/../_build"
  touch "$DIR/.env"

  log_step "Removing existing containers ..."
  _dockercompose down

  log_step "Rebuilding application container ..."
  _dockercompose build -q reportcard
  _dockercompose rm -f --stop reportcard

  log_step "Regenerating fixture data ..."
  pushd "$DIR" >/dev/null; python -m "datasources"; popd >/dev/null
  log "Done"

  log_step "Starting docker-compose stack ..."
  _dockercompose up --quiet-pull --force-recreate -d
  log "Done"
}

REBUILD=1
declare -a POSARGS

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-rebuild)
      REBUILD=0
      ;;
    *)
      POSARGS+=("$1")
      ;;
  esac
  shift
done

if [[ $REBUILD -eq 1 ]]; then
  rebuild
fi

for bin in ag entr; do
  if ! type -f "$bin" >/dev/null 2>&1; then
    log "ERROR: You must install the '$bin' tool to take advantage of the"
    log "watch functionality."
    log
    log "You can still run example reports with ./run.sh:"
    log "  ./run.sh --config-file examples/mysql.yaml"
    exit 1
  fi
done

log_step "Starting watcher ..."

ag -l -G 'examples|reportcard' . "$DIR/.." | entr "$DIR/run.sh" "${POSARGS[@]}"
