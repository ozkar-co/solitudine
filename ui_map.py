"""Dibujado del mapa, tiles, módulos y cables."""

from __future__ import annotations

import math
from enum import Enum

import pygame

from construction import BuildMode, BuildPreview
from simulation import Simulation
from ui_theme import (
    COL_BORDER,
    COL_CABLE,
    COL_CRITICAL,
    COL_CURSOR,
    COL_DIM,
    COL_FOG,
    COL_HABITAT,
    COL_PREVIEW_BAD,
    COL_PREVIEW_OK,
    DEPOSIT_OVERLAY,
    DEPOSIT_OVERLAY_ALPHA,
    MODULE_COLORS,
    TILE_COLORS,
    map_rect,
)
from world import Deposit, ModuleState, Tile, World


class MapLayer(Enum):
    TERRAIN = 0
    RESOURCES = 1


def _blend_color(
    base: tuple[int, int, int],
    overlay: tuple[int, int, int],
    alpha: float,
) -> tuple[int, int, int]:
    a = max(0.0, min(1.0, alpha))
    return tuple(int(base[c] * (1.0 - a) + overlay[c] * a) for c in range(3))


def _resource_overlay(world: World, i: int, tile: Tile) -> tuple[int, int, int] | None:
    amt = world.deposit_amounts[i]
    if amt <= 0:
        return None
    dep = Deposit(world.deposits[i])
    if dep in DEPOSIT_OVERLAY:
        return DEPOSIT_OVERLAY[dep]
    if tile == Tile.WATER:
        return DEPOSIT_OVERLAY[Deposit.WATER]
    return None


def _tile_draw_rect(sx: float, sy: float, px: float) -> pygame.Rect:
    x0 = math.floor(sx)
    y0 = math.floor(sy)
    x1 = math.ceil(sx + px)
    y1 = math.ceil(sy + px)
    return pygame.Rect(x0, y0, max(1, x1 - x0), max(1, y1 - y0))


def _draw_module(surf: pygame.Surface, tile_rect: pygame.Rect, mod) -> None:
    color = MODULE_COLORS.get(mod.kind.value, COL_HABITAT)
    pad = max(2, tile_rect.w // 5)
    inner = tile_rect.inflate(-pad, -pad)

    if mod.state == ModuleState.WAITING:
        pygame.draw.rect(surf, color, inner, 2)
        return

    if mod.state == ModuleState.BUILDING and mod.build_total > 0:
        h = max(1, int(inner.h * (mod.build_progress / mod.build_total)))
        bar = pygame.Rect(inner.x, inner.bottom - h, inner.w, h)
        pygame.draw.rect(surf, color, bar)
        pygame.draw.rect(surf, COL_DIM, inner, 1)
        return

    pygame.draw.rect(surf, color, inner)
    if mod.state == ModuleState.OFFLINE:
        pygame.draw.rect(surf, COL_CRITICAL, inner, 2)


def _draw_cables(
    surf: pygame.Surface,
    world: World,
    camera,
    rect: pygame.Rect,
    px: float,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
) -> None:
    nodes = set(world.cables)
    nodes.update((m.x, m.y) for m in world.modules)
    drawn: set[tuple[tuple[int, int], tuple[int, int]]] = set()
    width = max(1, int(px / 4))

    for ty in range(y0, y1):
        for tx in range(x0, x1):
            if (tx, ty) not in world.cables:
                continue
            sx, sy = camera.tile_to_screen(tx, ty, rect.x, rect.y, rect.w, rect.h)
            cx = sx + px / 2
            cy = sy + px / 2
            for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                nx, ny = tx + dx, ty + dy
                if (nx, ny) not in nodes:
                    continue
                edge = ((tx, ty), (nx, ny)) if (tx, ty) < (nx, ny) else ((nx, ny), (tx, ty))
                if edge in drawn:
                    continue
                drawn.add(edge)
                nsx, nsy = camera.tile_to_screen(nx, ny, rect.x, rect.y, rect.w, rect.h)
                pygame.draw.line(
                    surf,
                    COL_CABLE,
                    (cx, cy),
                    (nsx + px / 2, nsy + px / 2),
                    width,
                )


def draw_map(
    surf: pygame.Surface,
    world: World,
    sim: Simulation,
    camera,
    layer: MapLayer,
    cursor_x: int,
    cursor_y: int,
) -> int:
    rect = map_rect()
    prev_clip = surf.get_clip()
    surf.set_clip(rect)
    pygame.draw.rect(surf, (0, 0, 0), rect)

    px = camera.tile_px
    x0, y0, x1, y1 = camera.visible_tiles(rect.w, rect.h)
    drawn = 0

    for ty in range(y0, y1):
        for tx in range(x0, x1):
            sx, sy = camera.tile_to_screen(tx, ty, rect.x, rect.y, rect.w, rect.h)
            tile_rect = _tile_draw_rect(sx, sy, px)
            if not rect.colliderect(tile_rect):
                continue
            drawn += 1
            i = world.idx(tx, ty)

            if not world.explored[i]:
                pygame.draw.rect(surf, (0, 0, 0), tile_rect)
                continue

            tile = Tile(world.tiles[i])
            color = TILE_COLORS[tile]

            if layer == MapLayer.RESOURCES:
                overlay = _resource_overlay(world, i, tile)
                if overlay is not None:
                    color = _blend_color(color, overlay, DEPOSIT_OVERLAY_ALPHA)

            if not world.visible[i]:
                color = COL_FOG

            pygame.draw.rect(surf, color, tile_rect)

    _draw_cables(surf, world, camera, rect, px, x0, y0, x1, y1)

    for ty in range(y0, y1):
        for tx in range(x0, x1):
            if not world.explored[world.idx(tx, ty)]:
                continue
            sx, sy = camera.tile_to_screen(tx, ty, rect.x, rect.y, rect.w, rect.h)
            tile_rect = _tile_draw_rect(sx, sy, px)
            if not rect.colliderect(tile_rect):
                continue
            mod = world.module_at(tx, ty)
            if mod:
                _draw_module(surf, tile_rect, mod)

    build = sim.build
    if build.mode == BuildMode.PLACE and world.in_bounds(cursor_x, cursor_y):
        csx, csy = camera.tile_to_screen(
            cursor_x, cursor_y, rect.x, rect.y, rect.w, rect.h
        )
        cr = _tile_draw_rect(csx, csy, px)
        if rect.colliderect(cr):
            preview = build.preview(world, sim.stock, cursor_x, cursor_y)
            ok = preview == BuildPreview.OK
            pygame.draw.rect(surf, COL_PREVIEW_OK if ok else COL_PREVIEW_BAD, cr, 2)

    if world.in_bounds(cursor_x, cursor_y):
        csx, csy = camera.tile_to_screen(
            cursor_x, cursor_y, rect.x, rect.y, rect.w, rect.h
        )
        cr = _tile_draw_rect(csx, csy, px)
        if rect.colliderect(cr):
            pygame.draw.rect(surf, COL_CURSOR, cr, 2)

    pygame.draw.rect(surf, COL_BORDER, rect, 1)
    surf.set_clip(prev_clip)
    return drawn
