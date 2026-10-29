"""Carga y caché de sprites/fuentes pixel."""

from __future__ import annotations

from pathlib import Path

import pygame

from module_kind import ModuleKind
from world import Tile

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
TILE_FILES = {
    Tile.GROUND: "ground",
    Tile.WATER: "water",
    Tile.ROCK: "rock",
}
ICON_NAMES = (
    "o2",
    "water",
    "food",
    "power",
    "components",
    "mineral",
    "biomass",
    "chitin",
    "alloy",
    "core",
)

_tiles: dict[Tile, list[pygame.Surface]] = {}
_modules: dict[ModuleKind, pygame.Surface] = {}
_icons: dict[str, pygame.Surface] = {}
_tile_cache: dict[tuple[Tile, int, int], pygame.Surface] = {}
_module_cache: dict[tuple[ModuleKind, int], pygame.Surface] = {}
_font_sm: pygame.font.Font | None = None
_font_lg: pygame.font.Font | None = None
_easter_egg: pygame.Surface | None = None


def _load_image(path: Path) -> pygame.Surface:
    if not path.exists():
        raise FileNotFoundError(f"Falta el asset: {path}")
    return pygame.image.load(path).convert_alpha()


def load() -> None:
    """Carga todos los assets. Debe llamarse después de create_display()."""
    global _font_sm, _font_lg, _easter_egg

    _easter_egg = None

    for tile, name in TILE_FILES.items():
        paths = sorted((ASSETS_DIR / "tiles").glob(f"{name}_*.png"))
        if not paths:
            raise FileNotFoundError(f"Faltan tiles para {name}: {ASSETS_DIR / 'tiles'}")
        _tiles[tile] = [_load_image(p) for p in paths]

    for kind in ModuleKind:
        _modules[kind] = _load_image(ASSETS_DIR / "modules" / f"{kind.value}.png")

    for name in ICON_NAMES:
        _icons[name] = _load_image(ASSETS_DIR / "icons" / f"{name}.png")

    font_path = ASSETS_DIR / "fonts" / "VT323-Regular.ttf"
    if not font_path.exists():
        raise FileNotFoundError(f"Falta la fuente: {font_path}")
    _font_sm = pygame.font.Font(font_path, 16)
    _font_lg = pygame.font.Font(font_path, 24)

    egg_path = ASSETS_DIR / "credits" / "gatos.png"
    _easter_egg = _load_image(egg_path) if egg_path.exists() else None


def easter_egg() -> pygame.Surface | None:
    return _easter_egg


def font_sm() -> pygame.font.Font:
    assert _font_sm is not None, "assets.load() no fue llamado"
    return _font_sm


def font_lg() -> pygame.font.Font:
    assert _font_lg is not None, "assets.load() no fue llamado"
    return _font_lg


def tile(tile_kind: Tile, variant: int, px: int) -> pygame.Surface:
    variants = _tiles[tile_kind]
    base = variants[variant % len(variants)]
    if px == base.get_width():
        return base
    key = (tile_kind, variant % len(variants), px)
    cached = _tile_cache.get(key)
    if cached is None:
        cached = pygame.transform.scale(base, (px, px))
        _tile_cache[key] = cached
    return cached


def module(kind: ModuleKind, px: int) -> pygame.Surface:
    base = _modules[kind]
    if px == base.get_width():
        return base
    key = (kind, px)
    cached = _module_cache.get(key)
    if cached is None:
        cached = pygame.transform.scale(base, (px, px))
        _module_cache[key] = cached
    return cached


def icon(name: str) -> pygame.Surface:
    try:
        return _icons[name]
    except KeyError as exc:
        raise KeyError(f"Icono desconocido: {name}") from exc
