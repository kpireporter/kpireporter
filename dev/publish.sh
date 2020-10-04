#!/usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
export pypi_token="${PYPI_TOKEN:-$1}"

publish() {
  pushd "$1" >/dev/null
  rm -rf build dist
  echo "Publishing $1"
  python setup.py sdist bdist_wheel
  twine upload -u __token__ -p $pypi_token dist/*
  popd >/dev/null
}
export -f publish

publish $DIR/..
find $DIR/../plugins -maxdepth 1 -mindepth 1 -type d -exec bash -c 'publish {}' \;
