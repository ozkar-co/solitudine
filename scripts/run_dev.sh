#!/bin/bash
# Ejecutar en PC para probar sin PortMaster

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
fi

.venv/bin/python -m py_compile src/main.py src/gamepad.py
cd "$ROOT/src" && ../.venv/bin/python main.py
