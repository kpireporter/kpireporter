#!/usr/bin/env bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

_dockercompose() {
  docker-compose -f "$DIR/docker-compose.yaml" -p reportcard "$@"
}

# Perform rebuild
_dockercompose build reportcard
_dockercompose rm -f --stop reportcard
_dockercompose up -d

for bin in ag entr; do
  if ! type -f "$bin" >/dev/null 2>&1; then
    echo "You must install the '$bin' tool to take advantage of the watch"
    echo "functionality."
    exit 1
  fi
done

echo
echo "Starting watcher ..."
echo

# Can't use an alias here as the 'entr' binary needs to be able to resolve
# its command.
ag -l -G 'examples|reportcard' . "$DIR/.." \
  | entr docker-compose -f "$DIR/docker-compose.yaml" -p reportcard \
      exec reportcard "$@"
