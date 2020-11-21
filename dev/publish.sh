#!/usr/bin/env bash
set -e -u -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
export pypi_token="${PYPI_TOKEN:-}"

plugins="$@"

publish() {
  local root="$(realpath --relative-to=$DIR/.. $1)"
  local current_tag="$2"
  local next_tag="$3"

  if [[ "$root" != "." ]]; then
    commit_line="$root: $next_tag"
    tag_name="$next_tag+$(basename $root)"
  else
    commit_line="$next_tag"
    tag_name="$next_tag"
  fi

  if [[ "$current_tag" != "$next_tag" ]]; then
    echo "Publishing $root ($current_tag -> $next_tag) ..."
    pushd "$root" >/dev/null
    sed -i "s!$current_tag!$next_tag!g" setup.py
    git add setup.py
    git commit -m "$commit_line"
    git tag -a -m "$next_tag" "$tag_name"
    # git push --tags origin HEAD
    rm -rf build dist
    python setup.py sdist bdist_wheel
    # twine upload -u __token__ -p $pypi_token dist/*
    popd >/dev/null
  else
    echo "Skipping $root ($current_tag == $next_tag)"
  fi
}

publish_plugin() {
  local current_tag="$(git describe --tags $(git rev-list --tags -- $1))"
  local next_tag="$(reno -q --rel-notes-dir $1/releasenotes semver-next)"
  publish "$1" "$current_tag" "$next_tag"
}
export -f publish_plugin

if [[ -z "$plugins" ]]; then
  publish $DIR/..
  find $DIR/../plugins -maxdepth 1 -mindepth 1 -type d -exec bash -c 'publish_plugin {}' \;
else
  for plugin in $plugins; do publish_plugin plugins/$plugin; done
fi
