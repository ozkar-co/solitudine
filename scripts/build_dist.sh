#!/bin/bash
# Genera dist/ listo para copiar a la SD (roms/ports/)

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$ROOT/dist"

rm -rf "$DIST"
mkdir -p "$DIST/solitudine"

cp "$ROOT/src/main.py" "$DIST/solitudine/main.py"
cp "$ROOT/port/solitudine.gptk" "$DIST/solitudine/solitudine.gptk"
cp "$ROOT/port/Solitudine.sh" "$DIST/Solitudine.sh"
chmod +x "$DIST/Solitudine.sh"

echo "Listo: $DIST"
echo ""
echo "Copia el contenido de dist/ a la SD:"
echo "  dist/Solitudine.sh      → roms/ports/Solitudine.sh"
echo "  dist/solitudine/        → roms/ports/solitudine/"
