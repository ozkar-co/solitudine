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
    Tile.FOREST: "forest",
    Tile.SPROUT: "sprout",
}
COAST_SIDE_PREFIX = "coast_side_"
COAST_INNER_FILE = "coast_inner_corner.png"
COAST_OUTER_FILE = "coast_outer_border.png"
COAST_U_PREFIX = "coast_u_"
COAST_PARALLEL_PREFIX = "coast_parallel_"
COAST_ISLAND_PREFIX = "coast_island_"
COAST_INNER_OUTER_PREFIX = "coast_inner_outer_"
ICON_NAMES = (
    "o2",
    "water",
    "food",
    "power",
    "components",
    "mineral",
    "scrap",
    "cable",
    "wood",
    "coal",
    "fuel",
    "crystal",
    "biomass",
    "chitin",
    "alloy",
    "core",
)

_tiles: dict[Tile, list[pygame.Surface]] = {}
_coast_sides: list[pygame.Surface] = []
_coast_u: list[pygame.Surface] = []
_coast_parallel: list[pygame.Surface] = []
_coast_island: list[pygame.Surface] = []
_coast_inner_outer: list[pygame.Surface] = []
_coast_inner: pygame.Surface | None = None
_coast_outer: pygame.Surface | None = None
_modules: dict[ModuleKind, pygame.Surface] = {}
_icons: dict[str, pygame.Surface] = {}
_tile_cache: dict[tuple[Tile, int, int, int], pygame.Surface] = {}
_coast_cache: dict[tuple[str, int, int, int], pygame.Surface] = {}
_module_cache: dict[tuple[ModuleKind, int], pygame.Surface] = {}
_ruin: pygame.Surface | None = None
_ruin_cache: dict[int, pygame.Surface] = {}
_font_sm: pygame.font.Font | None = None
_font_lg: pygame.font.Font | None = None
_easter_egg: pygame.Surface | None = None

# A/B de fuentes: VT323-Regular.ttf o PixelOperator.ttf / PixelOperator-Bold.ttf.
FONT_BODY_FILE = "PixelOperator.ttf"
FONT_TITLE_FILE = "PixelOperator-Bold.ttf"
FONT_BODY_SIZE = 16
FONT_TITLE_SIZE = 24


def _load_image(path: Path) -> pygame.Surface:
    if not path.exists():
        raise FileNotFoundError(f"Falta el asset: {path}")
    return pygame.image.load(path).convert_alpha()


def load_font(filename: str, size: int) -> pygame.font.Font:
    path = ASSETS_DIR / "fonts" / filename
    if not path.exists():
        raise FileNotFoundError(f"Falta la fuente: {path}")
    return pygame.font.Font(path, size)


def load() -> None:
    """Carga todos los assets. Debe llamarse después de create_display()."""
    global _font_sm, _font_lg, _easter_egg, _ruin, _coast_inner, _coast_outer

    _easter_egg = None

    for tile, name in TILE_FILES.items():
        paths = sorted((ASSETS_DIR / "tiles").glob(f"{name}_*.png"))
        if not paths:
            raise FileNotFoundError(f"Faltan tiles para {name}: {ASSETS_DIR / 'tiles'}")
        _tiles[tile] = [_load_image(p) for p in paths]

    side_paths = sorted((ASSETS_DIR / "tiles").glob(f"{COAST_SIDE_PREFIX}*.png"))
    if not side_paths:
        raise FileNotFoundError(f"Faltan coast sides: {ASSETS_DIR / 'tiles'}")
    _coast_sides[:] = [_load_image(p) for p in side_paths]
    for prefix, target in (
        (COAST_U_PREFIX, _coast_u),
        (COAST_PARALLEL_PREFIX, _coast_parallel),
        (COAST_ISLAND_PREFIX, _coast_island),
        (COAST_INNER_OUTER_PREFIX, _coast_inner_outer),
    ):
        paths = sorted((ASSETS_DIR / "tiles").glob(f"{prefix}*.png"))
        if not paths:
            raise FileNotFoundError(f"Faltan coast tiles {prefix}: {ASSETS_DIR / 'tiles'}")
        target[:] = [_load_image(p) for p in paths]
    _coast_inner = _load_image(ASSETS_DIR / "tiles" / COAST_INNER_FILE)
    _coast_outer = _load_image(ASSETS_DIR / "tiles" / COAST_OUTER_FILE)

    _ruin = _load_image(ASSETS_DIR / "tiles" / "ruin_00.png")

    for kind in ModuleKind:
        _modules[kind] = _load_image(ASSETS_DIR / "modules" / f"{kind.value}.png")

    for name in ICON_NAMES:
        _icons[name] = _load_image(ASSETS_DIR / "icons" / f"{name}.png")

    _font_sm = load_font(FONT_BODY_FILE, FONT_BODY_SIZE)
    _font_lg = load_font(FONT_TITLE_FILE, FONT_TITLE_SIZE)

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


def tile(tile_kind: Tile, variant: int, px: int, rotation: int = 0) -> pygame.Surface:
    variants = _tiles[tile_kind]
    index = variant % len(variants)
    rot = rotation % 360
    key = (tile_kind, index, px, rot)
    cached = _tile_cache.get(key)
    if cached is None:
        base = variants[index]
        if rot:
            base = pygame.transform.rotate(base, rot)
        if px != base.get_width():
            base = pygame.transform.scale(base, (px, px))
        _tile_cache[key] = base
        cached = base
    return cached


def _coast_piece(
    kind: str,
    base: pygame.Surface,
    px: int,
    rotation: int,
    style: int = 0,
) -> pygame.Surface:
    rot = rotation % 360
    key = (kind, style, rot, px)
    cached = _coast_cache.get(key)
    if cached is None:
        piece = pygame.transform.rotate(base, rot) if rot else base
        if px != piece.get_width():
            piece = pygame.transform.scale(piece, (px, px))
        _coast_cache[key] = piece
        cached = piece
    return cached


def coast_side(px: int, rotation: int = 0, style: int = 0) -> pygame.Surface:
    base = _coast_sides[style % len(_coast_sides)]
    return _coast_piece("side", base, px, rotation, style % len(_coast_sides))


def coast_inner(px: int, rotation: int = 0) -> pygame.Surface:
    if _coast_inner is None:
        raise RuntimeError("Assets de costa no cargados")
    return _coast_piece("inner", _coast_inner, px, rotation)


def coast_outer(px: int, rotation: int = 0) -> pygame.Surface:
    if _coast_outer is None:
        raise RuntimeError("Assets de costa no cargados")
    return _coast_piece("outer", _coast_outer, px, rotation)


def _coast_variant(
    kind: str,
    variants: list[pygame.Surface],
    px: int,
    rotation: int,
    style: int,
) -> pygame.Surface:
    index = style % len(variants)
    return _coast_piece(kind, variants[index], px, rotation, index)


def coast_u(px: int, rotation: int = 0, style: int = 0) -> pygame.Surface:
    return _coast_variant("u", _coast_u, px, rotation, style)


def coast_parallel(px: int, rotation: int = 0, style: int = 0) -> pygame.Surface:
    return _coast_variant("parallel", _coast_parallel, px, rotation, style)


def coast_island(px: int, rotation: int = 0, style: int = 0) -> pygame.Surface:
    return _coast_variant("island", _coast_island, px, rotation, style)


def coast_inner_outer(px: int, rotation: int = 0, style: int = 0) -> pygame.Surface:
    return _coast_variant("inner_outer", _coast_inner_outer, px, rotation, style)


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


def ruin(px: int) -> pygame.Surface:
    assert _ruin is not None, "assets.load() no fue llamado"
    if px == _ruin.get_width():
        return _ruin
    cached = _ruin_cache.get(px)
    if cached is None:
        cached = pygame.transform.scale(_ruin, (px, px))
        _ruin_cache[px] = cached
    return cached


def icon(name: str) -> pygame.Surface:
    try:
        return _icons[name]
    except KeyError as exc:
        raise KeyError(f"Icono desconocido: {name}") from exc
