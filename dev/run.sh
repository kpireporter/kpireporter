#!/usr/bin/env bash
set -e -u -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
PROJ="$DIR/.."

pushd "$DIR" >/dev/null

usage() {
  cat <<USAGE
Usage: run.sh [-h] [--no-rebuild] [--watch] ARGS

Run a report against a local development Docker-Compose stack, with most
services mocked for testing. Good for exploring examples and playing with
output formatting. ARGS are passed on to the kpimailer script.

When the local development stack is running, the following services are
available:

  - MailHog (SMTP preview): localhost:8025
  - Nginx (HTTP preview): localhost:8080

Options:
  -h|--help: Prints this help message
  --no-rebuild: Skip a full rebuild of the Docker-Compose stack
  -w|--watch: Automatically re-run on changes

Examples:
  ./run.sh -c examples/mysql.yaml

  ./run.sh -w -c examples/mysql.yaml -c examples/outputs/smtp.yaml
USAGE
  exit 1
}

_dockercompose() {
  docker-compose -p kpireport "$@"
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
  mkdir -p "$PROJ/_build"
  touch "$DIR/.env"

  log_step "Removing existing containers ..."
  _dockercompose down

  log_step "Rebuilding application container ..."
  cat "$PROJ/plugins/"*/requirements.txt >"$PROJ/plugin-requirements.txt"
  _dockercompose build -q kpireport
  _dockercompose rm -f --stop kpireport

  log_step "Regenerating fixture data ..."
  tox -e examples
  log "Done"

  log_step "Starting docker-compose stack ..."
  _dockercompose up --quiet-pull --force-recreate -d
  log "Done"
}

REBUILD=1
WATCH=0
declare -a POSARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-rebuild)
      REBUILD=0
      ;;
    -w|--watch)
      WATCH=1
      ;;
    -h|--help)
      usage
      ;;
    *)
      POSARGS+=("$1")
      ;;
  esac
  shift
done

if [[ ${#POSARGS[@]} -eq 0 ]]; then
  usage
fi

if [[ $REBUILD -eq 1 ]]; then
  rebuild
fi

declare -a cmd=(
  docker-compose -f "$DIR/docker-compose.yaml" -p kpireport \
    exec -T kpireport wait-for mysql:3306 -t 60 -- python -m kpireport
)

if [[ $WATCH -eq 1 ]]; then
  for bin in ag entr; do
    if ! type -f "$bin" >/dev/null 2>&1; then
      log "ERROR: You must install the '$bin' tool to take advantage of the"
      log "watch functionality."
      exit 1
    fi
  done

  log_step "Starting watcher ..."
  ag -l -G 'examples|kpireport' . "$PROJ" | entr "${cmd[@]}" "${POSARGS[@]}"
else
  log_step "Running command kpireporter ${POSARGS[@]} ..."
  "${cmd[@]}" "${POSARGS[@]}"
fi
