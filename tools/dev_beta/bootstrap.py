"""Arranque compartido de las betas de PC."""

from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path


def _base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def run_beta(scale: float, tag: str, save_dir: str) -> int:
    base = _base_dir()
    if not getattr(sys, "frozen", False):
        root = Path(__file__).resolve().parents[2]
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))

    os.environ.setdefault("SOLITUDINE_SAVE_DIR", str(base / save_dir))
    log_name = "solitudine-beta.log" if not tag else f"solitudine-beta-{tag}.log"
    try:
        log = (base / log_name).open("w", encoding="utf-8", buffering=1)
    except OSError:
        log = None
    if log is not None:
        sys.stdout = log
        sys.stderr = log

    try:
        from game import run

        return run(dev=True, handheld=False, scale=scale)
    except Exception:
        traceback.print_exc()
        raise
