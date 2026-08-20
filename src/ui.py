"""Dibujado de HUD, mapa y panel."""

from __future__ import annotations

import math
from enum import Enum

import pygame

from config import (
    BOTTOM_BAR_H,
    HABITAT_COMPONENTS_CAP,
    HABITAT_FOOD_CAP,
    HABITAT_MINERAL_CAP,
    HABITAT_O2_CAP,
    HABITAT_POWER_CAP,
    HABITAT_WATER_CAP,
    PANEL_W,
    SCREEN_H,
    SCREEN_W,
    STORAGE_NETWORK_BONUS,
    TOP_BAR_H,
)
from construction import (
    BUILD_KINDS,
    BuildKind,
    BuildMode,
    kind_build_days,
    kind_cost,
)
from i18n import t
from logistics import storage_bonus
from module_flow import module_flow_lines
from module_power import format_energy_daily, module_energy_daily
from network import compute_connected
from resources import AlertLevel, ResourceId
from simulation import Simulation
from world import Deposit, ModuleState, Tile, World

# Colores retro CRT
COL_PANEL = (18, 28, 20)
COL_BORDER = (50, 130, 70)
COL_TEXT = (80, 255, 120)
COL_DIM = (45, 110, 60)
COL_WARN = (255, 200, 60)
COL_CRITICAL = (255, 80, 70)
COL_CURSOR = (255, 255, 180)
COL_HABITAT = (220, 200, 80)
COL_SOLAR = (255, 140, 40)
COL_RADAR = (80, 220, 220)
COL_EXTRACTOR = (60, 150, 230)
COL_GREENHOUSE = (90, 200, 70)
COL_MINE = (140, 110, 75)
COL_FABRICATOR = (200, 120, 180)
COL_STORAGE = (170, 170, 90)
COL_CABLE = (255, 230, 80)
COL_FOG = (20, 32, 24)
COL_PREVIEW_OK = (120, 255, 160)
COL_PREVIEW_BAD = (255, 100, 90)

TILE_COLORS = {
    Tile.GROUND: (55, 85, 45),
    Tile.WATER: (35, 75, 130),
    Tile.ROCK: (85, 88, 92),
}

DEPOSIT_OVERLAY = {
    Deposit.WATER: (40, 90, 160),
    Deposit.MINERAL: (120, 95, 55),
}

MODULE_COLORS = {
    "habitat": COL_HABITAT,
    "solar": COL_SOLAR,
    "radar": COL_RADAR,
    "extractor": COL_EXTRACTOR,
    "greenhouse": COL_GREENHOUSE,
    "mine": COL_MINE,
    "fabricator": COL_FABRICATOR,
    "storage": COL_STORAGE,
}


class MapLayer(Enum):
    TERRAIN = 0
    RESOURCES = 1


DEPOSIT_OVERLAY_ALPHA = 0.55


def _blend_color(
    base: tuple[int, int, int],
    overlay: tuple[int, int, int],
    alpha: float,
) -> tuple[int, int, int]:
    a = max(0.0, min(1.0, alpha))
    return tuple(int(base[c] * (1.0 - a) + overlay[c] * a) for c in range(3))


def _resource_overlay(world: World, i: int, tile: Tile) -> tuple[int, int, int] | None:
    """Color de depósito para capa Recursos (subterráneos y reserva en lagos)."""
    amt = world.deposit_amounts[i]
    if amt <= 0:
        return None
    dep = Deposit(world.deposits[i])
    if dep in DEPOSIT_OVERLAY:
        return DEPOSIT_OVERLAY[dep]
    if tile == Tile.WATER:
        return DEPOSIT_OVERLAY[Deposit.WATER]
    return None


def map_rect() -> pygame.Rect:
    return pygame.Rect(0, TOP_BAR_H, SCREEN_W - PANEL_W, SCREEN_H - TOP_BAR_H - BOTTOM_BAR_H)


def panel_rect() -> pygame.Rect:
    h = SCREEN_H - TOP_BAR_H - BOTTOM_BAR_H
    return pygame.Rect(SCREEN_W - PANEL_W, TOP_BAR_H, PANEL_W, h)


def _alert_color(level: AlertLevel) -> tuple[int, int, int]:
    if level == AlertLevel.CRITICAL:
        return COL_CRITICAL
    if level == AlertLevel.WARNING:
        return COL_WARN
    return COL_DIM


def _format_amount(value: float) -> str:
    return f"{value:.1f}"


def _format_days(days: float) -> str:
    if days >= 100:
        return "99+"
    return f"{days:.1f}"


def draw_top_bar(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
    sim: Simulation,
) -> None:
    pygame.draw.rect(surf, COL_PANEL, (0, 0, SCREEN_W, TOP_BAR_H))
    worst = sim.resources.worst_alert()
    bar_border = (
        COL_CRITICAL if worst == AlertLevel.CRITICAL else COL_WARN if worst == AlertLevel.WARNING else COL_BORDER
    )
    pygame.draw.line(surf, bar_border, (0, TOP_BAR_H - 1), (SCREEN_W, TOP_BAR_H - 1))
    if worst != AlertLevel.OK:
        pygame.draw.rect(surf, bar_border, (0, 0, SCREEN_W, TOP_BAR_H), 2)

    title = (
        f"{t('game.title')}  {t('planet.code')}  "
        f"{t('hud.day', day=sim.day)} {t('hud.hour', hour=sim.hour)}"
    )
    surf.blit(font.render(title, True, COL_TEXT), (8, 6))

    stats_x = SCREEN_W - 8
    mat = _format_amount(sim.stock.components)
    mat_s = font_sm.render(t("hud.components", value=mat), True, COL_DIM)
    stats_x -= mat_s.get_width() + 10
    surf.blit(mat_s, (stats_x, 9))

    o2 = _format_amount(sim.resources.o2)
    power = _format_amount(sim.resources.power)
    for text, level in (
        (t("hud.power", value=power), sim.resources.alert_level(ResourceId.POWER)),
        (t("hud.o2", value=o2), sim.resources.alert_level(ResourceId.O2)),
    ):
        stats_s = font_sm.render(text, True, _alert_color(level))
        stats_x -= stats_s.get_width() + 10
        surf.blit(stats_s, (stats_x, 9))


def draw_bottom_bar(surf: pygame.Surface, font_sm: pygame.font.Font, text: str) -> None:
    y = SCREEN_H - BOTTOM_BAR_H
    pygame.draw.rect(surf, COL_PANEL, (0, y, SCREEN_W, BOTTOM_BAR_H))
    pygame.draw.line(surf, COL_BORDER, (0, y), (SCREEN_W, y))
    surf.blit(font_sm.render(text, True, COL_DIM), (8, y + 5))


def _tile_draw_rect(sx: float, sy: float, px: float) -> pygame.Rect:
    x0 = math.floor(sx)
    y0 = math.floor(sy)
    x1 = math.ceil(sx + px)
    y1 = math.ceil(sy + px)
    return pygame.Rect(x0, y0, max(1, x1 - x0), max(1, y1 - y0))


def _panel_energy_line(mod) -> str:
    value = format_energy_daily(module_energy_daily(mod))
    return t("panel.energy", value=value)


def _panel_flow_line(key: str, value: float) -> str:
    if value > 0:
        return t(key, value=f"+{value:.1f}")
    return t(key, value=f"{value:.1f}")


def _network_bonus(world: World) -> float:
    return storage_bonus(world, compute_connected(world))


def _draw_module_inspection(
    surf: pygame.Surface,
    font_sm: pygame.font.Font,
    x: int,
    y: int,
    mod,
    world: World,
) -> int:
    _panel_line(surf, font_sm, x, y, t("panel.status", status=t(_module_status_key(mod))))
    y += 16
    _panel_line(surf, font_sm, x, y, _panel_energy_line(mod))
    y += 16
    if mod.kind == "storage":
        _panel_line(surf, font_sm, x, y, t("panel.storage_bonus", value=_format_amount(STORAGE_NETWORK_BONUS)))
        y += 16
    else:
        for key, value in module_flow_lines(mod, world):
            _panel_line(surf, font_sm, x, y, _panel_flow_line(key, value))
            y += 16
    if mod.buffer_cap > 0:
        _panel_line(
            surf,
            font_sm,
            x,
            y,
            t("panel.buffer", value=_format_amount(mod.buffer), cap=_format_amount(mod.buffer_cap)),
        )
        y += 16
    if mod.kind in ("extractor", "mine"):
        dep = Deposit.WATER if mod.kind == "extractor" else Deposit.MINERAL
        total = world.patch_deposit_total(mod.x, mod.y, dep)
        _panel_line(surf, font_sm, x, y, t("panel.patch_reserve", value=_format_amount(total)), COL_DIM)
        y += 16
    if mod.state == ModuleState.BUILDING and mod.build_total > 0:
        pct = 100.0 * mod.build_progress / mod.build_total
        _panel_line(surf, font_sm, x, y, t("panel.build_pct", pct=f"{pct:.0f}"))
        y += 16
    return y


def _module_status_key(mod) -> str:
    if mod.state == ModuleState.WAITING:
        return "status.waiting"
    if mod.state == ModuleState.BUILDING:
        return "status.building"
    if mod.state == ModuleState.OFFLINE:
        return "status.offline"
    return "status.online"


def _draw_module(surf: pygame.Surface, tile_rect: pygame.Rect, mod) -> None:
    color = MODULE_COLORS.get(mod.kind, COL_HABITAT)
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
            ok = build.preview_valid(world, sim.stock, cursor_x, cursor_y)
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


def _build_kind_label(kind: BuildKind) -> str:
    return {
        BuildKind.CABLE: t("build.cable"),
        BuildKind.SOLAR: t("build.solar"),
        BuildKind.RADAR: t("build.radar"),
        BuildKind.EXTRACTOR: t("build.extractor"),
        BuildKind.MINE: t("build.mine"),
        BuildKind.FABRICATOR: t("build.fabricator"),
        BuildKind.GREENHOUSE: t("build.greenhouse"),
        BuildKind.STORAGE: t("build.storage"),
    }[kind]


def draw_build_modal(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
    sim: Simulation,
) -> None:
    build = sim.build
    if build.mode not in (BuildMode.MENU, BuildMode.PLACE):
        return

    mrect = map_rect()
    overlay = pygame.Surface((mrect.w, mrect.h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 100))
    surf.blit(overlay, (mrect.x, mrect.y))

    pad_x, pad_y = 16, 12
    lines: list[tuple[str, tuple[int, int, int], pygame.font.Font]] = []
    lines.append((t("build.title"), COL_TEXT, font))

    if build.mode == BuildMode.MENU:
        lines.append(
            (t("build.components", value=_format_amount(sim.stock.components)), COL_DIM, font_sm)
        )
        for i, kind in enumerate(BUILD_KINDS):
            prefix = ">" if i == build.menu_index else " "
            label = _build_kind_label(kind)
            cost = _format_amount(kind_cost(kind))
            color = COL_TEXT if i == build.menu_index else COL_DIM
            lines.append((f"{prefix} {label} ({cost})", color, font_sm))
        lines.append((t("build.hint_menu"), COL_DIM, font_sm))
    else:
        lines.append((_build_kind_label(build.selected), COL_TEXT, font_sm))
        lines.append((t("build.cost", value=_format_amount(kind_cost(build.selected))), COL_DIM, font_sm))
        days = kind_build_days(build.selected)
        if days > 0:
            lines.append((t("build.time", days=f"{days:.1f}"), COL_DIM, font_sm))
        lines.append((t("build.hint_place"), COL_DIM, font_sm))

    w = pad_x * 2
    h = pad_y * 2
    rendered: list[tuple[pygame.Surface, tuple[int, int, int]]] = []
    for text, color, fnt in lines:
        s = fnt.render(text, True, color)
        rendered.append((s, color))
        w = max(w, s.get_width() + pad_x * 2)
        h += s.get_height() + (4 if fnt == font else 2)

    box = pygame.Rect(0, 0, w, h)
    box.center = (mrect.centerx, mrect.centery)
    pygame.draw.rect(surf, COL_PANEL, box)
    pygame.draw.rect(surf, COL_BORDER, box, 2)

    y = box.y + pad_y
    for s, _color in rendered:
        surf.blit(s, (box.centerx - s.get_width() // 2, y))
        y += s.get_height() + (4 if s.get_height() > 20 else 2)


def draw_pause_modal(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
    *,
    show_hint: bool,
) -> None:
    mrect = map_rect()
    pad_x, pad_y = 18, 12
    title_s = font.render(t("pause.title"), True, COL_TEXT)
    hint_s = font_sm.render(t("pause.hint"), True, COL_DIM) if show_hint else None

    w = title_s.get_width() + pad_x * 2
    h = title_s.get_height() + pad_y * 2
    if hint_s is not None:
        w = max(w, hint_s.get_width() + pad_x * 2)
        h += hint_s.get_height() + 6

    box = pygame.Rect(0, 0, w, h)
    box.center = (mrect.centerx, mrect.centery)

    pygame.draw.rect(surf, COL_PANEL, box)
    pygame.draw.rect(surf, COL_BORDER, box, 2)

    y = box.y + pad_y
    surf.blit(title_s, (box.centerx - title_s.get_width() // 2, y))
    y += title_s.get_height() + 4
    if hint_s is not None:
        surf.blit(hint_s, (box.centerx - hint_s.get_width() // 2, y))


def draw_game_over(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
    sim: Simulation,
) -> None:
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surf.blit(overlay, (0, 0))

    title = font.render(t("game_over.title"), True, COL_CRITICAL)
    surf.blit(title, ((SCREEN_W - title.get_width()) // 2, SCREEN_H // 2 - 36))

    cause = font_sm.render(t(sim.death_cause), True, COL_TEXT)
    surf.blit(cause, ((SCREEN_W - cause.get_width()) // 2, SCREEN_H // 2 - 6))

    hint = font_sm.render(t("game_over.restart"), True, COL_DIM)
    surf.blit(hint, ((SCREEN_W - hint.get_width()) // 2, SCREEN_H // 2 + 24))


def draw_panel(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
    world: World,
    sim: Simulation,
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

    if (sel_x, sel_y) in world.cables:
        _panel_line(surf, font_sm, rect.x + 8, y, t("panel.cable"))
        y += 16
        _panel_line(surf, font_sm, rect.x + 8, y, t("panel.energy", value="0.0"))
        return

    mod = world.module_at(sel_x, sel_y)
    if mod:
        name = t("module.habitat") if mod.kind == "habitat" else t(f"module.{mod.kind}")
        _panel_line(surf, font_sm, rect.x + 8, y, t("panel.module", name=name))
        y += 18
        if mod.kind == "habitat":
            for key, value in module_flow_lines(mod, world):
                _panel_line(surf, font_sm, rect.x + 8, y, _panel_flow_line(key, value))
                y += 16
            _draw_habitat_resources(surf, font_sm, rect, y, sim, world)
        else:
            _draw_module_inspection(surf, font_sm, rect.x + 8, y, mod, world)
        return

    tile = world.tile_at(sel_x, sel_y)
    if tile is not None:
        names = {
            Tile.GROUND: t("tile.ground"),
            Tile.WATER: t("tile.water"),
            Tile.ROCK: t("tile.rock"),
        }
        _panel_line(surf, font_sm, rect.x + 8, y, t("panel.type", type=names[tile]))
        y += 16
        if tile == Tile.WATER:
            amt = world.deposit_amount_at(sel_x, sel_y)
            if amt > 0:
                _panel_line(
                    surf,
                    font_sm,
                    rect.x + 8,
                    y,
                    t("panel.deposit_amount", value=_format_amount(amt)),
                    COL_DIM,
                )
                y += 16
        dep = world.deposit_at(sel_x, sel_y)
        if dep and dep != Deposit.NONE and world.deposit_amount_at(sel_x, sel_y) > 0:
            dep_name = t("deposit.water") if dep == Deposit.WATER else t("deposit.mineral")
            _panel_line(surf, font_sm, rect.x + 8, y, t("panel.deposit", name=dep_name))
            y += 16
            _panel_line(surf, font_sm, rect.x + 8, y, t("panel.deposit_amount", value=_format_amount(world.deposit_amount_at(sel_x, sel_y))), COL_DIM)


def _panel_line(surf, font, x, y, text, color: tuple[int, int, int] = COL_TEXT) -> None:
    surf.blit(font.render(text, True, color), (x, y))


def _draw_habitat_resources(
    surf: pygame.Surface,
    font_sm: pygame.font.Font,
    rect: pygame.Rect,
    y: int,
    sim: Simulation,
    world: World,
) -> None:
    bonus = _network_bonus(world)
    labels = {
        ResourceId.O2: t("resource.o2"),
        ResourceId.POWER: t("resource.power"),
        ResourceId.WATER: t("resource.water"),
        ResourceId.FOOD: t("resource.food"),
    }
    caps = {
        ResourceId.O2: HABITAT_O2_CAP + bonus,
        ResourceId.POWER: HABITAT_POWER_CAP + bonus,
        ResourceId.WATER: HABITAT_WATER_CAP + bonus,
        ResourceId.FOOD: HABITAT_FOOD_CAP + bonus,
    }
    for resource in ResourceId:
        amount = _format_amount(sim.resources.amount(resource))
        cap = _format_amount(caps[resource])
        days_s = _format_days(sim.resources.days_left(resource))
        line = t("panel.resource_cap", name=labels[resource], value=amount, cap=cap, days=days_s)
        _panel_line(surf, font_sm, rect.x + 8, y, line, _alert_color(sim.resources.alert_level(resource)))
        y += 16

    line = t(
        "panel.material_cap",
        name=t("resource.mineral"),
        value=_format_amount(sim.stock.mineral),
        cap=_format_amount(HABITAT_MINERAL_CAP + bonus),
    )
    _panel_line(surf, font_sm, rect.x + 8, y, line, COL_DIM)
    y += 16
    line = t(
        "panel.material_cap",
        name=t("resource.components"),
        value=_format_amount(sim.stock.components),
        cap=_format_amount(HABITAT_COMPONENTS_CAP + bonus),
    )
    _panel_line(surf, font_sm, rect.x + 8, y, line, COL_DIM)
    y += 16

    worst = sim.resources.worst_alert()
    if worst != AlertLevel.OK:
        y += 4
        alert_key = "alert.critical" if worst == AlertLevel.CRITICAL else "alert.warning"
        _panel_line(surf, font_sm, rect.x + 8, y, t(alert_key), _alert_color(worst))
