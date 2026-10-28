"""Día/noche por dithering, contrarrestado por fuentes de luz.

La luz es puramente visual: no altera producción ni consumo. El hábitat
ilumina desde el inicio y las lámparas amplían la zona sin dithering.
"""

from __future__ import annotations

import pygame

from module_defs import module_def
from module_kind import ModuleKind
from world import ModuleState, World

_LEVELS = 8
_MAX_DENSITY = 0.65
_COLORKEY = (255, 0, 255)
_DITHER_COLOR = (8, 12, 28)

_BAYER8 = (
    (0, 32, 8, 40, 2, 34, 10, 42),
    (48, 16, 56, 24, 50, 18, 58, 26),
    (12, 44, 4, 36, 14, 46, 6, 38),
    (60, 28, 52, 20, 62, 30, 54, 22),
    (3, 35, 11, 43, 1, 33, 9, 41),
    (51, 19, 59, 27, 49, 17, 57, 25),
    (15, 47, 7, 39, 13, 45, 5, 37),
    (63, 31, 55, 23, 61, 29, 53, 21),
)

_patterns: dict[tuple[int, int], pygame.Surface] = {}


def light_sources(world: World, connected: set[tuple[int, int]]) -> list[tuple[int, int, int]]:
    """(x, y, radio) de hábitat y lámparas activas. Sin demanda ni consumo."""
    sources: list[tuple[int, int, int]] = []
    for mod in world.modules:
        radius = module_def(mod.kind).light_radius
        if radius <= 0:
            continue
        if mod.kind != ModuleKind.HABITAT:
            if mod.state != ModuleState.ONLINE or (mod.x, mod.y) not in connected:
                continue
        sources.append((mod.x, mod.y, radius))
    return sources


def light_at(x: int, y: int, natural: float, sources: list[tuple[int, int, int]]) -> float:
    best = natural
    for sx, sy, radius in sources:
        dx = x - sx
        dy = y - sy
        d2 = dx * dx + dy * dy
        r2 = radius * radius
        if d2 > r2:
            continue
        value = 1.0 - d2 / r2
        if value > best:
            best = value
    return min(1.0, best)


def tile_level(x: int, y: int, natural: float, sources: list[tuple[int, int, int]]) -> int:
    """0 = sin dithering, 7 = noche plena. La luz resta dithering."""
    return max(0, min(_LEVELS - 1, round((1.0 - light_at(x, y, natural, sources)) * (_LEVELS - 1))))


def dither_pattern(level: int, size: int) -> pygame.Surface | None:
    if level <= 0:
        return None
    key = (level, size)
    cached = _patterns.get(key)
    if cached is not None:
        return cached

    density = _MAX_DENSITY * level / (_LEVELS - 1)
    surf = pygame.Surface((size, size))
    surf.fill(_COLORKEY)
    for y in range(size):
        row = _BAYER8[y % 8]
        for x in range(size):
            if (row[x % 8] + 0.5) / 64.0 <= density:
                surf.set_at((x, y), _DITHER_COLOR)
    surf.set_colorkey(_COLORKEY)
    _patterns[key] = surf
    return surf
