#!/usr/bin/env bash
set -e -u -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
export pypi_token="${PYPI_TOKEN:-}"
# Navigate to root
pushd "$DIR/.." >/dev/null

export PLUGIN=""
export ALL_PLUGINS=no
export DRY_RUN=no

_maybe() {
  if [[ "$DRY_RUN" == "yes" ]]; then
    echo "$@"
  else
    "$@"
  fi
}

publish_path() {
  local root="$(realpath --relative-to=. $1)"
  local current_tag="$2"
  local next_tag="$3"
  local version_file="$4"

  if [[ "$root" != "." ]]; then
    current_version="$(cut -d/ -f2 <<<"$current_tag")"
    next_version="$(cut -d/ -f2 <<<"$next_tag")"
    commit_line="$(basename $root): $next_version"
  else
    current_version="$current_tag"
    next_version="$next_tag"
    commit_line="$next_version"
  fi

  if [[ "$current_version" != "$next_version" ]]; then
    echo "Publishing $root ($current_version -> $next_version) ..."
    pushd "$root" >/dev/null
    _maybe sed -i.bak -E "s!(version\s*=\s*\"?)[^\"]*(\"?)!\1$next_version\2!gi" "$version_file"
    _maybe git add "$version_file"
    _maybe git commit -m "$commit_line"
    _maybe git tag -a -m "$next_tag" "$next_tag"
    _maybe git push --tags origin HEAD
    rm -rf build dist
    if [[ -f pyproject.toml ]]; then
      python -m build
    else
      python setup.py -q sdist bdist_wheel
    fi
    _maybe twine upload -u __token__ -p $pypi_token dist/*
    popd >/dev/null
  else
    echo "Skipping $root ($current_tag == $next_tag)"
  fi
}

publish_plugin() {
  local current_tag="$(git tag -l "$(basename $1)/*" | tail -n1)"
  local next_tag="${2:-$(reno -q --rel-notes-dir $(realpath --relative-to="$PWD" "$1/releasenotes") semver-next)}"
  publish_path "$1" "$current_tag" "$next_tag" "$(find $1 \( -name setup.py -o -name setup.cfg \) -exec basename {} \; | sort | head -n1)"
}

publish_root() {
  local current_tag="$(git tag -l '[0-9].[0-9].[0-9]' | tail -n1)"
  local next_tag="${1:-$(reno -q semver-next)}"
  publish_path "." "$current_tag" "$next_tag" kpireport/version.py
}

cmd_publish() {
  local next_tag="${1:-}"
  if [[ -n "$PLUGIN" ]]; then
    publish_plugin plugins/$PLUGIN "$next_tag"
  else
    publish_root "$next_tag"
    if [[ "$ALL_PLUGINS" == "yes" ]]; then
      export -f publish_plugin
      export -f publish_path
      export -f _maybe
      find $DIR/../plugins -maxdepth 1 -mindepth 1 -type d -exec bash -c 'publish_plugin {}' \;
    fi
  fi
}

cmd_note() {
  declare -a reno_args=()
  if [[ -n "$PLUGIN" ]]; then
    reno_args+=(--rel-notes-dir "plugins/$PLUGIN/releasenotes")
  fi
  reno "${reno_args[@]}" "$@"
}

usage() {
  cat <<USAGE
release.sh [--plugin PLUGIN] CMD

Options:
  --plugin PLUGIN: target operation to a specific plugin
  --all: publish all changed packages
  --dry-run: don't perform destructive operations (applies to 'publish' only.)

Commands:
  publish: publish a new version of the module(s).
  note: manage release notes. This wraps the ``reno`` utility.
USAGE
  exit 1
}

cmd=""
declare -a posargs
while [[ $# -gt 0 ]]; do
  case "$1" in
    note)
      cmd=cmd_note
      ;;
    publish)
      cmd=cmd_publish
      ;;
    --plugin)
      export PLUGIN="$2"
      shift
      ;;
    --all)
      ALL_PLUGINS=yes
      ;;
    --dry-run)
      export DRY_RUN=yes
      ;;
    -h|--help)
      usage
      ;;
    *)
      posargs+=("$1")
      ;;
  esac
  shift
done

if [[ -z "$cmd" ]]; then usage; fi

tox -e dev echo Setup env
source .tox/dev/bin/activate
"$cmd" "${posargs[@]}"
