"""Dibujado de HUD, mapa y panel."""

from __future__ import annotations

import math
from enum import Enum

import pygame

from config import BOTTOM_BAR_H, PANEL_W, SCREEN_H, SCREEN_W, TOP_BAR_H
from i18n import t
from world import Tile, World

# Colores retro CRT
COL_BG = (12, 20, 14)
COL_PANEL = (18, 28, 20)
COL_BORDER = (50, 130, 70)
COL_TEXT = (80, 255, 120)
COL_DIM = (45, 110, 60)
COL_CURSOR = (255, 255, 180)
COL_HABITAT = (220, 200, 80)
COL_FOG = (20, 32, 24)

TILE_COLORS = {
    Tile.GROUND: (55, 85, 45),
    Tile.WATER: (35, 75, 130),
    Tile.ROCK: (85, 88, 92),
}


class MapLayer(Enum):
    TERRAIN = 0
    RESOURCES = 1
    WATER = 2


def map_rect() -> pygame.Rect:
    return pygame.Rect(0, TOP_BAR_H, SCREEN_W - PANEL_W, SCREEN_H - TOP_BAR_H - BOTTOM_BAR_H)


def panel_rect() -> pygame.Rect:
    h = SCREEN_H - TOP_BAR_H - BOTTOM_BAR_H
    return pygame.Rect(SCREEN_W - PANEL_W, TOP_BAR_H, PANEL_W, h)


def draw_top_bar(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
    day: int,
) -> None:
    pygame.draw.rect(surf, COL_PANEL, (0, 0, SCREEN_W, TOP_BAR_H))
    pygame.draw.line(surf, COL_BORDER, (0, TOP_BAR_H - 1), (SCREEN_W, TOP_BAR_H - 1))
    title = f"{t('game.title')}  {t('planet.code')}  {t('hud.day', day=day)}"
    surf.blit(font.render(title, True, COL_TEXT), (8, 6))
    stats = f"{t('hud.o2', value='--')}  {t('hud.power', value='--')}"
    stats_s = font_sm.render(stats, True, COL_DIM)
    surf.blit(stats_s, (SCREEN_W - stats_s.get_width() - 8, 9))


def draw_bottom_bar(surf: pygame.Surface, font_sm: pygame.font.Font, text: str) -> None:
    y = SCREEN_H - BOTTOM_BAR_H
    pygame.draw.rect(surf, COL_PANEL, (0, y, SCREEN_W, BOTTOM_BAR_H))
    pygame.draw.line(surf, COL_BORDER, (0, y), (SCREEN_W, y))
    surf.blit(font_sm.render(text, True, COL_DIM), (8, y + 5))


def _tile_draw_rect(sx: float, sy: float, px: float) -> pygame.Rect:
    """Rect contiguo — evita huecos/solapes con zoom fraccional."""
    x0 = math.floor(sx)
    y0 = math.floor(sy)
    x1 = math.ceil(sx + px)
    y1 = math.ceil(sy + px)
    return pygame.Rect(x0, y0, max(1, x1 - x0), max(1, y1 - y0))


def draw_map(
    surf: pygame.Surface,
    world: World,
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
            if layer == MapLayer.WATER and tile == Tile.WATER:
                color = (50, 110, 180)
            elif layer == MapLayer.RESOURCES:
                color = tuple(min(255, c + 15) for c in color)

            if not world.visible[i]:
                color = COL_FOG

            pygame.draw.rect(surf, color, tile_rect)

            mod = world.module_at(tx, ty)
            if mod and world.visible[i]:
                pad = max(2, tile_rect.w // 5)
                inner = tile_rect.inflate(-pad, -pad)
                pygame.draw.rect(surf, COL_HABITAT, inner)

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


def draw_dev_debug(
    surf: pygame.Surface,
    font_sm: pygame.font.Font,
    *,
    fps: float,
    frame_ms: float,
    tiles_drawn: int,
    gen_ms: float,
    held: frozenset[str],
    keymap: str,
    zoom_pct: float,
) -> None:
    """Overlay solo modo dev."""
    from gamepad import format_actions

    rect = map_rect()
    lines = [
        f"FPS {fps:4.1f}  frame {frame_ms:5.1f}ms  tiles {tiles_drawn}  zoom {zoom_pct:.0f}%",
        f"gen {gen_ms:.0f}ms  held: {format_actions(held)}",
    ]
    y = rect.y + 4
    for line in lines:
        surf.blit(font_sm.render(line, True, (120, 180, 255)), (rect.x + 4, y))
        y += 14
    y += 4
    for line in keymap.splitlines():
        surf.blit(font_sm.render(line, True, (90, 140, 200)), (rect.x + 4, y))
        y += 13


def draw_panel(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
    world: World,
    sel_x: int | None,
    sel_y: int | None,
    layer: MapLayer,
) -> None:
    rect = panel_rect()
    pygame.draw.rect(surf, COL_PANEL, rect)
    pygame.draw.line(surf, COL_BORDER, (rect.x, rect.y), (rect.x, rect.bottom))

    y = rect.y + 10
    surf.blit(font.render(t("panel.title"), True, COL_TEXT), (rect.x + 8, y))
    y += 24
    layer_name = {
        MapLayer.TERRAIN: t("layer.terrain"),
        MapLayer.RESOURCES: t("layer.resources"),
        MapLayer.WATER: t("layer.water"),
    }[layer]
    surf.blit(font_sm.render(layer_name, True, COL_DIM), (rect.x + 8, y))
    y += 22

    if sel_x is None or sel_y is None:
        _panel_line(surf, font_sm, rect.x + 8, y, t("panel.empty"))
        return

    if not world.explored[world.idx(sel_x, sel_y)]:
        _panel_line(surf, font_sm, rect.x + 8, y, t("tile.unknown"))
        return

    _panel_line(surf, font_sm, rect.x + 8, y, t("panel.coords", x=sel_x, y=sel_y))
    y += 18

    mod = world.module_at(sel_x, sel_y)
    if mod:
        name = t("module.habitat") if mod.kind == "habitat" else mod.kind
        _panel_line(surf, font_sm, rect.x + 8, y, t("panel.module", name=name))
        y += 18
        _panel_line(surf, font_sm, rect.x + 8, y, t("panel.status", status=t("status.ok")))
        return

    tile = world.tile_at(sel_x, sel_y)
    if tile is not None:
        names = {
            Tile.GROUND: t("tile.ground"),
            Tile.WATER: t("tile.water"),
            Tile.ROCK: t("tile.rock"),
        }
        _panel_line(surf, font_sm, rect.x + 8, y, t("panel.type", type=names[tile]))


def _panel_line(surf, font, x, y, text) -> None:
    surf.blit(font.render(text, True, COL_TEXT), (x, y))
