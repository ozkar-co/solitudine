#!/bin/bash
# Genera dist/ listo para copiar a la SD (roms/ports/)

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$ROOT/dist"
RUNTIME="port/runtime/pygame-ce_2.5.6_python_3.12.8.squashfs"

rm -rf "$DIST"
mkdir -p "$DIST/solitudine/runtime"

cp "$ROOT/src/main.py" "$ROOT/src/gamepad.py" "$DIST/solitudine/"
cp "$ROOT/port/Solitudine.sh" "$DIST/Solitudine.sh"
chmod +x "$DIST/Solitudine.sh"

if [ -f "$ROOT/$RUNTIME" ]; then
  cp "$ROOT/$RUNTIME" "$DIST/solitudine/runtime/"
  echo "Runtime incluido en dist/"
else
  echo "AVISO: sin runtime. Ejecuta ./scripts/fetch_runtime.sh primero."
fi

echo ""
echo "Listo: $DIST"
