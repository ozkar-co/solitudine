"""Textos parametrizados por idioma."""

from __future__ import annotations

import json
from pathlib import Path

_LOCALES = Path(__file__).parent / "locales"
_strings: dict[str, str] = {}


def load(lang: str = "es") -> None:
    global _strings
    path = _LOCALES / f"{lang}.json"
    with path.open(encoding="utf-8") as f:
        _strings = json.load(f)


def t(key: str, **kwargs: object) -> str:
    text = _strings.get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text
