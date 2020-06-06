#!/usr/bin/env bash
export SCP_IDENTITY_FILE="${SCP_IDENTITY_FILE:-/tmp/dummy_id_rsa}"
touch "$SCP_IDENTITY_FILE"

cat plugins/*/requirements.txt >plugin-requirements.txt
