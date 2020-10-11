#!/usr/bin/env bash
set -e -u -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
PROJ="$DIR/.."

# Allow overriding the name of the docker image to use in the compose env.
export DOCKER_IMAGE="${DOCKER_IMAGE:-diurnalist/kpireporter}"
export DOCKER_TAG=dev

pushd "$DIR" >/dev/null

usage() {
  cat <<USAGE
Usage: run.sh [-h] [--no-rebuild] [--watch] ARGS

Run a report against a local development Docker-Compose stack, with most
services mocked for testing. Good for exploring examples and playing with
output formatting. ARGS are passed on to the kpireport script.

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
  for _ in {1..80}; do printf "*" >&2; done
  log
  log "$@"
  for _ in {1..80}; do printf "*" >&2; done
  log
}

log_and_run() {
  log "+ Executing: $@"
  "$@"
}

rebuild() {
  mkdir -p "$PROJ/_build"
  touch "$DIR/.env"

  log_step "Removing existing containers ..."
  _dockercompose down

  log_step "Rebuilding application container ..."
  cat "$PROJ/plugins/"*/requirements.txt >"$PROJ/plugin-requirements.txt"
  declare -a build_cmd=()
  build_cmd+=(docker build -f "$PROJ/docker/Dockerfile" --target dev --tag "$DOCKER_IMAGE:$DOCKER_TAG")
  if [[ "${CI:-false}" == "true" ]]; then
    build_cmd+=(--cache-from "type=local,src=/tmp/.buildx-cache")
    build_cmd+=(--cache-to "type=local,dest=/tmp/.buildx-cache")
    build_cmd+=(--build-arg "python_version=$PYTHON_VERSION")
    build_cmd+=(--load)
    build_cmd+=(--platform amd64)
  fi
  build_cmd+=("$PROJ")
  log_and_run "${build_cmd[@]}"
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
  echo 0 >"$DIR/.kpireport_ready_signal"
  rebuild
  # This is a bit of a hack; it's possible to `exec` inside a container before
  # the entrypoint has finished execution on the initial command. The
  # entrypoint is responsible for doing local installs of all the plugins,
  # so if an exec comes in too quickly, it can fail due to missing deps.
  log_step "Waiting for container to install all local dependencies ..."
  timeout=120
  attempts=0
  while [[ $(cat "$DIR/.kpireport_ready_signal") -eq 0 ]]; do
    sleep 1
    attempts=$((attempts + 1))
    [[ $attempts -gt $timeout ]] && {
      echo "Failed to get ready signal after ${timeout}s"
      exit 1
    }
  done
  echo "Waited ${attempts}s"
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
  log_step "Running command kpireporter " "${POSARGS[@]}" " ..."
  "${cmd[@]}" "${POSARGS[@]}"
fi
