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
    COL_BUILD_BAR,
    COL_CABLE,
    COL_CRITICAL,
    COL_CURSOR,
    COL_DIM,
    COL_FOG,
    COL_PREVIEW_BAD,
    COL_PREVIEW_OK,
    COL_SELECT,
    DEPOSIT_OVERLAY,
    DEPOSIT_OVERLAY_ALPHA,
    map_rect,
)
from module_defs import module_def
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


_COAST_SIDES = (
    ("n", 0, -1, 270),
    ("e", 1, 0, 180),
    ("s", 0, 1, 90),
    ("w", -1, 0, 0),
)
_COAST_CORNERS = (
    ("nw", "n", "w", -1, -1, 0),
    ("sw", "s", "w", -1, 1, 90),
    ("se", "s", "e", 1, 1, 180),
    ("ne", "n", "e", 1, -1, 270),
)
_COAST_DIAGONALS = (
    ("nw", -1, -1),
    ("ne", 1, -1),
    ("se", 1, 1),
    ("sw", -1, 1),
)
_CORNER_OPPOSITE = {"nw": "se", "se": "nw", "ne": "sw", "sw": "ne"}
_SIDE_ROTATION = {"n": 270, "e": 180, "s": 90, "w": 0}
_LAND_SIDE_ROTATION = {"w": 0, "s": 90, "e": 180, "n": 270}


def coast_overlay_plan(world: World, tx: int, ty: int) -> list[tuple[str, int]]:
    """Piezas de costa para un tile: (tipo, rotación).

    Bases: side con agua al oeste; inner/outer/inner_outer en NW; U con tierra
    al oeste; parallel con agua al norte y al sur. Las rotaciones se aplican en
    el render.
    """
    water = {
        name
        for name, dx, dy, _rot in _COAST_SIDES
        if world.tile_at(tx + dx, ty + dy) == Tile.WATER
    }
    diag = {
        name
        for name, dx, dy in _COAST_DIAGONALS
        if world.tile_at(tx + dx, ty + dy) == Tile.WATER
    }

    if len(water) == 4:
        return [("island", 0)]
    if len(water) == 3:
        land = ({"n", "e", "s", "w"} - water).pop()
        return [("u", _LAND_SIDE_ROTATION[land])]
    if len(water) == 2:
        if water == {"n", "s"}:
            return [("parallel", 0)]
        if water == {"e", "w"}:
            return [("parallel", 90)]
        corner = next(c for c in _COAST_CORNERS if c[1] in water and c[2] in water)
        name, _a, _b, _dx, _dy, rot = corner
        opposite = _CORNER_OPPOSITE[name]
        # Dos lados ortogonales de agua: siempre inner. El outer solo puede
        # aparecer en la esquina opuesta, donde ambos ortogonales son tierra.
        if opposite in diag:
            return [("inner_outer", rot)]
        return [("inner", rot)]

    if len(water) == 1:
        name = next(iter(water))
        _dx, _dy, rot = next((dx, dy, rot) for n, dx, dy, rot in _COAST_SIDES if n == name)
        plan: list[tuple[str, int]] = [("side", rot)]
        for cname, a, b, _cdx, _cdy, crot in _COAST_CORNERS:
            if a in water or b in water:
                continue
            if cname in diag:
                plan.append(("outer", crot))
        return plan

    return [
        ("outer", crot)
        for cname, _a, _b, _dx, _dy, crot in _COAST_CORNERS
        if cname in diag
    ]


def _draw_coast(
    surf: pygame.Surface,
    world: World,
    tx: int,
    ty: int,
    tile_rect: pygame.Rect,
    tile: Tile,
) -> None:
    if tile != Tile.GROUND:
        return
    for kind, rotation in coast_overlay_plan(world, tx, ty):
        if kind == "side":
            piece = ui_assets.coast_side(tile_rect.w, rotation)
        elif kind == "inner":
            piece = ui_assets.coast_inner(tile_rect.w, rotation)
        elif kind == "outer":
            piece = ui_assets.coast_outer(tile_rect.w, rotation)
        elif kind == "u":
            piece = ui_assets.coast_u(tile_rect.w, rotation)
        elif kind == "parallel":
            piece = ui_assets.coast_parallel(tile_rect.w, rotation)
        elif kind == "island":
            piece = ui_assets.coast_island(tile_rect.w, rotation)
        elif kind == "inner_outer":
            piece = ui_assets.coast_inner_outer(tile_rect.w, rotation)
        else:
            continue
        surf.blit(piece, tile_rect.topleft)


_OVERLAY_CACHE: dict[tuple[tuple[int, int, int], int], pygame.Surface] = {}
_DISABLED_CACHE: dict[int, pygame.Surface] = {}


def _tint_overlay(color: tuple[int, int, int], size: int) -> pygame.Surface:
    key = (color, size)
    overlay = _OVERLAY_CACHE.get(key)
    if overlay is None:
        overlay = pygame.Surface((size, size), pygame.SRCALPHA)
        overlay.fill((*color, int(255 * DEPOSIT_OVERLAY_ALPHA)))
        _OVERLAY_CACHE[key] = overlay
    return overlay


def _disabled_overlay(size: int) -> pygame.Surface:
    overlay = _DISABLED_CACHE.get(size)
    if overlay is None:
        overlay = pygame.Surface((size, size), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        _DISABLED_CACHE[size] = overlay
    return overlay


def _draw_module(surf: pygame.Surface, tile_rect: pygame.Rect, mod) -> None:
    sprite = ui_assets.module(mod.kind, tile_rect.w)
    if mod.state in (ModuleState.WAITING, ModuleState.BUILDING):
        ghost = sprite.copy()
        ghost.set_alpha(110)
        surf.blit(ghost, tile_rect.topleft)
    else:
        surf.blit(sprite, tile_rect.topleft)

    if module_def(mod.kind).can_toggle and not mod.enabled:
        surf.blit(_disabled_overlay(tile_rect.w), tile_rect.topleft)
        pygame.draw.rect(surf, COL_DIM, tile_rect, 1)

    if mod.state == ModuleState.WAITING:
        pygame.draw.rect(surf, COL_DIM, tile_rect, 2)
        return

    if mod.state == ModuleState.BUILDING and mod.build_total > 0:
        h = max(1, int(tile_rect.h * (mod.build_progress / mod.build_total)))
        bar = pygame.Rect(tile_rect.x, tile_rect.bottom - h, tile_rect.w, h)
        pygame.draw.rect(surf, COL_BUILD_BAR, bar)
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
    select_x: int | None = None,
    select_y: int | None = None,
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
            rotation = ((h >> 8) & 3) * 90 if tile in (Tile.GROUND, Tile.ROCK, Tile.WATER) else 0
            surf.blit(ui_assets.tile(tile, h, tile_rect.w, rotation), tile_rect.topleft)

            if layer == MapLayer.RESOURCES:
                overlay = _resource_overlay(world, i, tile)
                if overlay is not None:
                    surf.blit(_tint_overlay(overlay, tile_rect.w), tile_rect.topleft)

            _draw_coast(surf, world, tx, ty, tile_rect, tile)

            if world.has_ruin(tx, ty):
                surf.blit(ui_assets.ruin(tile_rect.w), tile_rect.topleft)

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
            preview = build.preview(world, sim.resources, cursor_x, cursor_y)
            ok = preview == BuildPreview.OK
            pygame.draw.rect(surf, COL_PREVIEW_OK if ok else COL_PREVIEW_BAD, cr, 2)

    if select_x is not None and select_y is not None and world.in_bounds(select_x, select_y):
        ssx, ssy = camera.tile_to_screen(
            select_x, select_y, rect.x, rect.y, rect.w, rect.h
        )
        sr = _tile_draw_rect(ssx, ssy, px)
        if rect.colliderect(sr):
            pygame.draw.rect(surf, COL_SELECT, sr, 2)

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
