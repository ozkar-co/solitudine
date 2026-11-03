#!/usr/bin/env python3
"""Build de beta para PC — siempre dev + 2x, sin opciones."""

from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path


def _base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def _prepare_environment() -> Path:
    base = _base_dir()
    if not getattr(sys, "frozen", False):
        root = Path(__file__).resolve().parents[2]
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
    os.environ.setdefault("SOLITUDINE_SAVE_DIR", str(base / "saves"))
    try:
        log = (base / "solitudine-beta.log").open("w", encoding="utf-8", buffering=1)
    except OSError:
        return base
    sys.stdout = log
    sys.stderr = log
    return base


def main() -> int:
    _prepare_environment()
    try:
        from game import run

        return run(dev=True, handheld=False, scale=2)
    except Exception:
        traceback.print_exc()
        raise


if __name__ == "__main__":
    raise SystemExit(main())
