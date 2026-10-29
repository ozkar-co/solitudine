"""Minimapa cacheado con vista de cámara y cursor."""

from __future__ import annotations

import pygame

from config import WORLD_SIZE
from ui_layout import map_rect
from ui_theme import COL_BORDER, COL_CABLE, COL_CURSOR, COL_PANEL, TILE_COLORS
from world import Tile, World

_MINIMAP_PX = 112
_SOURCE = 128

_surface: pygame.Surface | None = None
_scaled: pygame.Surface | None = None
_world_id: int | None = None
_region: tuple[int, int, int] = (0, 0, WORLD_SIZE)
_last_bounds: tuple[int, int, int, int, int] | None = None


def _explored_region(world: World) -> tuple[int, int, int]:
    margin = 12
    min_x = max(0, world.expl_min_x - margin)
    min_y = max(0, world.expl_min_y - margin)
    max_x = min(world.size, world.expl_max_x + margin + 1)
    max_y = min(world.size, world.expl_max_y + margin + 1)
    span = max(64, max_x - min_x, max_y - min_y)
    cx = (min_x + max_x) // 2
    cy = (min_y + max_y) // 2
    min_x = max(0, min(world.size - span, cx - span // 2))
    min_y = max(0, min(world.size - span, cy - span // 2))
    return min_x, min_y, span


def _rebuild(world: World) -> None:
    global _surface, _scaled, _world_id, _region
    min_x, min_y, span = _explored_region(world)
    _region = (min_x, min_y, span)
    step = span / _SOURCE
    surf = pygame.Surface((_SOURCE, _SOURCE))
    surf.fill((4, 7, 5))
    for my in range(_SOURCE):
        wy = min(world.size - 1, int(min_y + my * step))
        for mx in range(_SOURCE):
            wx = min(world.size - 1, int(min_x + mx * step))
            i = world.idx(wx, wy)
            if not world.explored[i]:
                continue
            surf.set_at((mx, my), TILE_COLORS[Tile(world.tiles[i])])
    _surface = surf
    _scaled = pygame.transform.scale(surf, (_MINIMAP_PX, _MINIMAP_PX))
    _world_id = id(world)


def _project(x: int, y: int) -> tuple[int, int]:
    min_x, min_y, span = _region
    return (
        int((x - min_x) / span * _MINIMAP_PX),
        int((y - min_y) / span * _MINIMAP_PX),
    )


def draw_minimap(
    screen: pygame.Surface,
    world: World,
    camera,
    *,
    cursor_x: int,
    cursor_y: int,
    visible: bool,
) -> None:
    global _last_bounds
    if not visible:
        return

    bounds = (world.explored_version, world.expl_min_x, world.expl_min_y, world.expl_max_x, world.expl_max_y)
    if _world_id != id(world) or _surface is None or bounds != _last_bounds:
        _rebuild(world)
        _last_bounds = bounds

    rect = map_rect()
    x = rect.right - _MINIMAP_PX - 4
    y = rect.y + 4

    frame = pygame.Surface((_MINIMAP_PX + 4, _MINIMAP_PX + 4), pygame.SRCALPHA)
    frame.fill((*COL_PANEL, 220))
    screen.blit(frame, (x - 2, y - 2))
    screen.blit(_scaled, (x, y))
    pygame.draw.rect(screen, COL_BORDER, (x - 2, y - 2, _MINIMAP_PX + 4, _MINIMAP_PX + 4), 1)

    prev_clip = screen.get_clip()
    screen.set_clip(pygame.Rect(x, y, _MINIMAP_PX, _MINIMAP_PX))
    for cx, cy in world.cables:
        if not world.explored[world.idx(cx, cy)]:
            continue
        mx, my = _project(cx, cy)
        if 0 <= mx < _MINIMAP_PX and 0 <= my < _MINIMAP_PX:
            screen.set_at((x + mx, y + my), COL_CABLE)

    for rx, ry in world.ruins:
        if not world.explored[world.idx(rx, ry)]:
            continue
        mx, my = _project(rx, ry)
        if 0 <= mx < _MINIMAP_PX and 0 <= my < _MINIMAP_PX:
            screen.set_at((x + mx, y + my), (170, 130, 80))

    for mod in world.modules:
        mx, my = _project(mod.x, mod.y)
        if 0 <= mx < _MINIMAP_PX and 0 <= my < _MINIMAP_PX:
            pygame.draw.rect(screen, (200, 255, 200), (x + mx - 1, y + my - 1, 3, 3))

    x0, y0, x1, y1 = camera.visible_tiles(rect.w, rect.h)
    vx, vy = _project(x0, y0)
    vx2, vy2 = _project(x1, y1)
    pygame.draw.rect(
        screen,
        COL_CURSOR,
        (x + vx, y + vy, max(1, vx2 - vx), max(1, vy2 - vy)),
        1,
    )

    mx, my = _project(cursor_x, cursor_y)
    if 0 <= mx < _MINIMAP_PX and 0 <= my < _MINIMAP_PX:
        pygame.draw.rect(screen, (255, 255, 255), (x + mx, y + my, 2, 2))
    screen.set_clip(prev_clip)
