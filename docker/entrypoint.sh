#!/usr/bin/env bash
# Install any PyPI packages in /plugins
find /plugins -maxdepth 1 -mindepth 1 -type d -exec pip install {} \;

exec python -m kpireport "$@"
