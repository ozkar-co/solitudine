#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

if [ ! -d .venv-beta ]; then
  python3 -m venv .venv-beta
fi
.venv-beta/bin/python -m pip install -q -r requirements.txt -r tools/dev_beta/requirements.txt
.venv-beta/bin/python tools/dev_beta/build.py
