#!/bin/bash
# Descarga el runtime pygame-ce para aarch64 (R36S / PortMaster)

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUNTIME_DIR="$ROOT/port/runtime"
FILE="pygame-ce_2.5.6_python_3.12.8.squashfs"
URL="https://github.com/viniciusfs/pygame-ce-runtime/releases/download/v0.3.0/$FILE"

mkdir -p "$RUNTIME_DIR"

if [ -f "$RUNTIME_DIR/$FILE" ]; then
  echo "Ya existe: $RUNTIME_DIR/$FILE"
  exit 0
fi

echo "Descargando runtime (~22 MB)..."
curl -L --progress-bar -o "$RUNTIME_DIR/$FILE" "$URL"
echo "Listo: $RUNTIME_DIR/$FILE"
