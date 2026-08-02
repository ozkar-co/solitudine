#!/bin/bash
# Genera dist/ listo para copiar a la SD (roms/ports/)

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$ROOT/dist"
RUNTIME="port/runtime/pygame-ce_2.5.6_python_3.12.8.squashfs"

rm -rf "$DIST"
mkdir -p "$DIST/solitudine/runtime"

cp "$ROOT/src/main.py" "$DIST/solitudine/main.py"
cp "$ROOT/port/solitudine.gptk" "$DIST/solitudine/solitudine.gptk"
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
echo ""
echo "Copia el contenido de dist/ a la SD:"
echo "  dist/Solitudine.sh           → roms/ports/Solitudine.sh"
echo "  dist/solitudine/             → roms/ports/solitudine/"
