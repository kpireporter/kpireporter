#!/usr/bin/env bash
# The entrypoint for the "dev" Docker image target ensures that the locally-
# mounted code for kpireport and the plugins are installed and linked.
pip install -e .
for plugin in $(find plugins -maxdepth 1 -mindepth 1 -type d); do
  pip install -e $plugin
done
echo 1 >/root/kpireport_ready_signal
# Start a new interactive shell
exec bash
