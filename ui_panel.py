"""Panel lateral: inspección, hábitat y modo colocar."""

from __future__ import annotations

import pygame

from config import HOURS_PER_DAY, STORAGE_NETWORK_BONUS
from construction import (
    BuildKind,
    BuildMode,
    BuildPreview,
    kind_build_days,
    kind_cost,
    module_kind_for,
    preview_locale_key,
)
from i18n import t
from logistics import network_caps
from module_defs import ModuleContext, ModuleKind, module_def
from module_flow import module_flow_lines
from module_power import format_energy_daily, module_energy_daily
from network import get_connected
from resources import AlertLevel, ResourceId
from simulation import Simulation
from ui_map import MapLayer
from ui_theme import (
    COL_BORDER,
    COL_DIM,
    COL_PANEL,
    COL_PREVIEW_BAD,
    COL_PREVIEW_OK,
    COL_TEXT,
    alert_color,
    format_amount,
    format_days,
    panel_rect,
)
from world import Deposit, ModuleState, Tile, World


def _module_ctx(sim: Simulation, world: World, mod) -> ModuleContext:
    connected_set = get_connected(world)
    connected = mod.kind == ModuleKind.HABITAT or (mod.x, mod.y) in connected_set
    return ModuleContext(
        world=world,
        hour_float=sim.day_progress * HOURS_PER_DAY,
        connected=connected,
    )


def _panel_line(surf, font, x, y, text, color: tuple[int, int, int] = COL_TEXT) -> None:
    surf.blit(font.render(text, False, color), (x, y))


def _panel_flow_line(key: str, value: float) -> str:
    if value > 0:
        return t(key, value=f"+{value:.1f}")
    return t(key, value=f"{value:.1f}")


def _panel_energy_line(mod, sim: Simulation, world: World) -> str:
    ctx = _module_ctx(sim, world, mod)
    value = format_energy_daily(
        module_energy_daily(mod, world, hour_float=ctx.hour_float, connected=ctx.connected)
    )
    return t("panel.energy", value=value)


def _module_status_key(mod) -> str:
    if not mod.enabled:
        return "status.disabled"
    if mod.state == ModuleState.WAITING:
        return "status.waiting"
    if mod.state == ModuleState.BUILDING:
        return "status.building"
    if mod.state == ModuleState.OFFLINE:
        return "status.offline"
    return "status.online"


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
        BuildKind.LAMP: t("build.lamp"),
    }[kind]


def _draw_build_place(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
    rect: pygame.Rect,
    sim: Simulation,
    world: World,
    cursor_x: int,
    cursor_y: int,
) -> None:
    y = rect.y + 10
    build = sim.build
    surf.blit(font.render(t("build.title"), False, COL_TEXT), (rect.x + 8, y))
    y += 26
    _panel_line(surf, font_sm, rect.x + 8, y, _build_kind_label(build.selected))
    y += 18
    _panel_line(surf, font_sm, rect.x + 8, y, t("build.cost", value=format_amount(kind_cost(build.selected))))
    y += 16
    days = kind_build_days(build.selected)
    if days > 0:
        _panel_line(surf, font_sm, rect.x + 8, y, t("build.time", days=f"{days:.1f}"))
        y += 16
    if build.selected != BuildKind.CABLE:
        radius = module_def(module_kind_for(build.selected)).light_radius
        if radius > 0:
            _panel_line(surf, font_sm, rect.x + 8, y, t("build.light_radius", radius=radius))
            y += 16
    if world.in_bounds(cursor_x, cursor_y):
        preview = build.preview(world, sim.stock, cursor_x, cursor_y)
        ok = preview == BuildPreview.OK
        color = COL_PREVIEW_OK if ok else COL_PREVIEW_BAD
        _panel_line(surf, font_sm, rect.x + 8, y, t("panel.coords", x=cursor_x, y=cursor_y), color)
        y += 16
        _panel_line(
            surf,
            font_sm,
            rect.x + 8,
            y,
            t(preview_locale_key(preview)),
            color,
        )
        y += 16
    y += 4
    _panel_line(surf, font_sm, rect.x + 8, y, t("build.hint_place"), COL_DIM)


def _draw_module_inspection(
    surf: pygame.Surface,
    font_sm: pygame.font.Font,
    x: int,
    y: int,
    mod,
    world: World,
    sim: Simulation,
) -> int:
    ctx = _module_ctx(sim, world, mod)
    _panel_line(surf, font_sm, x, y, t("panel.status", status=t(_module_status_key(mod))))
    y += 16
    _panel_line(surf, font_sm, x, y, _panel_energy_line(mod, sim, world))
    y += 16
    radius = module_def(mod.kind).light_radius
    if radius > 0:
        _panel_line(surf, font_sm, x, y, t("panel.light_radius", radius=radius))
        y += 16
    if mod.kind == ModuleKind.STORAGE:
        _panel_line(surf, font_sm, x, y, t("panel.storage_bonus", value=format_amount(STORAGE_NETWORK_BONUS)))
        y += 16
    else:
        for key, value in module_flow_lines(
            mod, world, hour_float=ctx.hour_float, connected=ctx.connected
        ):
            _panel_line(surf, font_sm, x, y, _panel_flow_line(key, value))
            y += 16
    if mod.buffer_cap > 0:
        _panel_line(
            surf,
            font_sm,
            x,
            y,
            t("panel.buffer", value=format_amount(mod.buffer), cap=format_amount(mod.buffer_cap)),
        )
        y += 16
    if mod.kind in (ModuleKind.EXTRACTOR, ModuleKind.MINE):
        dep = Deposit.WATER if mod.kind == ModuleKind.EXTRACTOR else Deposit.MINERAL
        total = world.patch_deposit_total(mod.x, mod.y, dep)
        _panel_line(surf, font_sm, x, y, t("panel.patch_reserve", value=format_amount(total)), COL_DIM)
        y += 16
    if mod.state == ModuleState.BUILDING and mod.build_total > 0:
        pct = 100.0 * mod.build_progress / mod.build_total
        _panel_line(surf, font_sm, x, y, t("panel.build_pct", pct=f"{pct:.0f}"))
        y += 16
    return y


def _draw_habitat_resources(
    surf: pygame.Surface,
    font_sm: pygame.font.Font,
    rect: pygame.Rect,
    y: int,
    sim: Simulation,
    world: World,
) -> None:
    nc = network_caps(world, get_connected(world))
    labels = {
        ResourceId.O2: t("resource.o2"),
        ResourceId.POWER: t("resource.power"),
        ResourceId.WATER: t("resource.water"),
        ResourceId.FOOD: t("resource.food"),
    }
    caps = {
        ResourceId.O2: nc.o2,
        ResourceId.POWER: nc.power,
        ResourceId.WATER: nc.water,
        ResourceId.FOOD: nc.food,
    }
    for resource in ResourceId:
        amount = format_amount(sim.resources.amount(resource))
        cap = format_amount(caps[resource])
        days_s = format_days(sim.resources.days_left(resource))
        line = t("panel.resource_cap", name=labels[resource], value=amount, cap=cap, days=days_s)
        _panel_line(surf, font_sm, rect.x + 8, y, line, alert_color(sim.resources.alert_level(resource)))
        y += 16

    line = t(
        "panel.material_cap",
        name=t("resource.mineral"),
        value=format_amount(sim.stock.mineral),
        cap=format_amount(nc.mineral),
    )
    _panel_line(surf, font_sm, rect.x + 8, y, line, COL_DIM)
    y += 16
    line = t(
        "panel.material_cap",
        name=t("resource.components"),
        value=format_amount(sim.stock.components),
        cap=format_amount(nc.components),
    )
    _panel_line(surf, font_sm, rect.x + 8, y, line, COL_DIM)
    y += 16

    worst = sim.resources.worst_alert()
    if worst != AlertLevel.OK:
        y += 4
        alert_key = "alert.critical" if worst == AlertLevel.CRITICAL else "alert.warning"
        _panel_line(surf, font_sm, rect.x + 8, y, t(alert_key), alert_color(worst))


def draw_panel(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
    world: World,
    sim: Simulation,
    sel_x: int | None,
    sel_y: int | None,
    layer: MapLayer,
    *,
    cursor_x: int = 0,
    cursor_y: int = 0,
) -> None:
    rect = panel_rect()
    pygame.draw.rect(surf, COL_PANEL, rect)
    pygame.draw.line(surf, COL_BORDER, (rect.x, rect.y), (rect.x, rect.bottom))

    build = sim.build
    if build.mode == BuildMode.PLACE:
        _draw_build_place(surf, font, font_sm, rect, sim, world, cursor_x, cursor_y)
        return

    y = rect.y + 10
    surf.blit(font.render(t("panel.title"), False, COL_TEXT), (rect.x + 8, y))
    y += 24
    layer_name = {
        MapLayer.TERRAIN: t("layer.terrain"),
        MapLayer.RESOURCES: t("layer.resources"),
    }[layer]
    surf.blit(font_sm.render(layer_name, False, COL_DIM), (rect.x + 8, y))
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
        name = t("module.habitat") if mod.kind == ModuleKind.HABITAT else t(f"module.{mod.kind.value}")
        _panel_line(surf, font_sm, rect.x + 8, y, t("panel.module", name=name))
        y += 18
        if mod.kind == ModuleKind.HABITAT:
            ctx = _module_ctx(sim, world, mod)
            for key, value in module_flow_lines(
                mod, world, hour_float=ctx.hour_float, connected=ctx.connected
            ):
                _panel_line(surf, font_sm, rect.x + 8, y, _panel_flow_line(key, value))
                y += 16
            _panel_line(surf, font_sm, rect.x + 8, y, _panel_energy_line(mod, sim, world))
            y += 16
            _draw_habitat_resources(surf, font_sm, rect, y, sim, world)
        else:
            _draw_module_inspection(surf, font_sm, rect.x + 8, y, mod, world, sim)
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
                    t("panel.deposit_amount", value=format_amount(amt)),
                    COL_DIM,
                )
                y += 16
        dep = world.deposit_at(sel_x, sel_y)
        if dep and dep != Deposit.NONE and world.deposit_amount_at(sel_x, sel_y) > 0:
            dep_name = t("deposit.water") if dep == Deposit.WATER else t("deposit.mineral")
            _panel_line(surf, font_sm, rect.x + 8, y, t("panel.deposit", name=dep_name))
            y += 16
            _panel_line(
                surf,
                font_sm,
                rect.x + 8,
                y,
                t("panel.deposit_amount", value=format_amount(world.deposit_amount_at(sel_x, sel_y))),
                COL_DIM,
            )
