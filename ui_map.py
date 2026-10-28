"""Dibujado del mapa, tiles, módulos y cables."""

from __future__ import annotations

from enum import Enum

import pygame

import ui_assets
from construction import BuildMode, BuildPreview
from network import get_connected
from simulation import Simulation
from daylight import natural_light
from ui_night import dither_pattern, light_sources, tile_level
from ui_theme import (
    COL_BORDER,
    COL_CABLE,
    COL_CRITICAL,
    COL_CURSOR,
    COL_DIM,
    COL_FOG,
    COL_PREVIEW_BAD,
    COL_PREVIEW_OK,
    DEPOSIT_OVERLAY,
    DEPOSIT_OVERLAY_ALPHA,
    map_rect,
)
from world import Deposit, ModuleState, Tile, World


class MapLayer(Enum):
    TERRAIN = 0
    RESOURCES = 1


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


def _tile_draw_rect(sx: float, sy: float, px: int) -> pygame.Rect:
    return pygame.Rect(round(sx), round(sy), px, px)


_OVERLAY_CACHE: dict[tuple[tuple[int, int, int], int], pygame.Surface] = {}


def _tint_overlay(color: tuple[int, int, int], size: int) -> pygame.Surface:
    key = (color, size)
    overlay = _OVERLAY_CACHE.get(key)
    if overlay is None:
        overlay = pygame.Surface((size, size), pygame.SRCALPHA)
        overlay.fill((*color, int(255 * DEPOSIT_OVERLAY_ALPHA)))
        _OVERLAY_CACHE[key] = overlay
    return overlay


def _draw_module(surf: pygame.Surface, tile_rect: pygame.Rect, mod) -> None:
    sprite = ui_assets.module(mod.kind, tile_rect.w)
    if mod.state in (ModuleState.WAITING, ModuleState.BUILDING):
        ghost = sprite.copy()
        ghost.set_alpha(110)
        surf.blit(ghost, tile_rect.topleft)
    else:
        surf.blit(sprite, tile_rect.topleft)

    if mod.state == ModuleState.WAITING:
        pygame.draw.rect(surf, COL_DIM, tile_rect, 2)
        return

    if mod.state == ModuleState.BUILDING and mod.build_total > 0:
        h = max(1, int(tile_rect.h * (mod.build_progress / mod.build_total)))
        bar = pygame.Rect(tile_rect.x, tile_rect.bottom - h, tile_rect.w, h)
        pygame.draw.rect(surf, COL_CABLE, bar)
        pygame.draw.rect(surf, COL_DIM, tile_rect, 1)
        return

    if mod.state == ModuleState.OFFLINE:
        pygame.draw.rect(surf, COL_CRITICAL, tile_rect, 2)


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
    natural = natural_light(sim.day_progress)
    sources = light_sources(world, get_connected(world)) if natural < 0.999 else []
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

            if not world.visible[i]:
                pygame.draw.rect(surf, COL_FOG, tile_rect)
                continue

            h = (tx * 374761393 + ty * 668265263) & 0xFFFFFFFF
            h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
            surf.blit(ui_assets.tile(tile, h, tile_rect.w), tile_rect.topleft)

            if layer == MapLayer.RESOURCES:
                overlay = _resource_overlay(world, i, tile)
                if overlay is not None:
                    surf.blit(_tint_overlay(overlay, tile_rect.w), tile_rect.topleft)

            if natural < 0.999:
                level = tile_level(tx, ty, natural, sources)
                pattern = dither_pattern(level, tile_rect.w)
                if pattern is not None:
                    surf.blit(pattern, tile_rect.topleft)

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
