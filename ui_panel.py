"""Panel lateral: inspección, hábitat y modo colocar."""

from __future__ import annotations

import pygame

from config import (
    HOURS_PER_DAY,
    SOLAR_HOUR_END,
    SOLAR_HOUR_START,
    STORAGE_NETWORK_BONUS,
)
from construction import (
    BuildKind,
    BuildMode,
    BuildPreview,
    kind_build_days,
    kind_cost,
    module_kind_for,
    preview_locale_key,
)
from daylight import darkness
from i18n import t
from logistics import network_caps
from module_defs import ModuleContext, ModuleKind, effective_flow, module_def
from module_flow import module_flow_lines
from module_power import format_energy_daily, module_energy_daily
from network import get_connected
from resources import AlertLevel, ResourceId
from simulation import Simulation
import ui_assets
from ui_map import MapLayer
from ui_theme import (
    COL_BORDER,
    COL_CRITICAL,
    COL_DIM,
    COL_PANEL,
    COL_PREVIEW_BAD,
    COL_PREVIEW_OK,
    COL_TEXT,
    COL_WARN,
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


def module_debug_lines(sim: Simulation, world: World, mod) -> list[str]:
    """Flujos nominales del módulo — solo para el overlay de debug."""
    ctx = _module_ctx(sim, world, mod)
    lines = [
        _panel_flow_line(key, value)
        for key, value in module_flow_lines(
            mod, world, hour_float=ctx.hour_float, connected=ctx.connected
        )
    ]
    lines.append(_panel_energy_line(mod, sim, world))
    return lines


def _output_space(pool: float, cap: float, mod=None) -> float:
    local = 0.0
    if mod is not None and mod.buffer_cap > 0:
        local = max(0.0, mod.buffer_cap - mod.buffer)
    return local + max(0.0, cap - pool)


def _module_status_key(mod, sim: Simulation, world: World, caps) -> str:
    if not mod.enabled:
        return "status.disabled"
    if mod.state == ModuleState.WAITING:
        return "status.waiting"
    if mod.state == ModuleState.BUILDING:
        return "status.building"
    if mod.state == ModuleState.OFFLINE:
        return "status.offline"

    kind = mod.kind
    defn = module_def(kind)
    if kind == ModuleKind.HABITAT:
        return "status.life_support"
    if kind == ModuleKind.STORAGE:
        return "status.storage"
    if kind == ModuleKind.LAMP and darkness(sim.day_progress) <= 0.0:
        return "status.idle"
    if defn.nominal.power < 0.0:
        if sim.power_factor <= 0.0:
            return "status.no_power"
        if sim.power_factor < 0.999:
            return "status.low_power"

    if kind in (ModuleKind.EXTRACTOR, ModuleKind.MINE):
        dep = Deposit.WATER if kind == ModuleKind.EXTRACTOR else Deposit.MINERAL
        if not world.patch_has_deposit(mod.x, mod.y, dep):
            return "status.no_deposit"
        if kind == ModuleKind.EXTRACTOR:
            space = _output_space(sim.resources.water, caps.water, mod)
        else:
            space = _output_space(sim.stock.mineral, caps.mineral, mod)
        if space <= 0.0:
            return "status.no_output"
        return "status.producing"

    if kind == ModuleKind.GREENHOUSE:
        food_space = _output_space(sim.resources.food, caps.food, mod)
        o2_space = max(0.0, caps.o2 - sim.resources.o2)
        if sim.resources.water <= 0.0:
            return "status.no_water"
        if food_space <= 0.0 and o2_space <= 0.0:
            return "status.no_output"
        if food_space <= 0.0:
            return "status.o2_only"
        return "status.producing"

    if kind == ModuleKind.FABRICATOR:
        if sim.stock.mineral <= 0.0:
            return "status.no_mineral"
        if _output_space(sim.stock.components, caps.components, mod) <= 0.0:
            return "status.no_output"
        return "status.producing"

    if kind == ModuleKind.ELECTROLYZER:
        if sim.resources.water <= 0.0:
            return "status.no_water"
        if sim.resources.o2 >= caps.o2:
            return "status.o2_full"
        return "status.producing"

    if kind == ModuleKind.CONDENSER:
        if sim.resources.water >= caps.water:
            return "status.water_full"
        return "status.producing"

    if kind == ModuleKind.SOLAR:
        hour = sim.day_progress * HOURS_PER_DAY
        if not (SOLAR_HOUR_START <= hour < SOLAR_HOUR_END):
            return "status.night"
        if sim.resources.power >= caps.power:
            return "status.power_full"
        return "status.producing"

    if kind == ModuleKind.LAMP:
        if darkness(sim.day_progress) <= 0.0:
            return "status.idle"
        return "status.lighting"

    if kind == ModuleKind.LABORATORY:
        return "status.researching" if sim.research.active is not None else "status.lab_idle"
    if kind == ModuleKind.RADAR:
        return "status.scanning"
    return "status.producing"


def _status_color(key: str) -> tuple[int, int, int]:
    if key == "status.no_power":
        return COL_CRITICAL
    if key in ("status.offline",):
        return COL_CRITICAL
    if key in (
        "status.waiting",
        "status.building",
        "status.low_power",
        "status.no_water",
        "status.no_mineral",
        "status.no_deposit",
        "status.o2_only",
    ):
        return COL_WARN
    if key in (
        "status.disabled",
        "status.no_output",
        "status.o2_full",
        "status.water_full",
        "status.power_full",
        "status.night",
        "status.idle",
        "status.lab_idle",
    ):
        return COL_DIM
    return COL_TEXT


def _panel_wrapped(
    surf: pygame.Surface,
    font: pygame.font.Font,
    x: int,
    y: int,
    text: str,
    width: int,
    color: tuple[int, int, int] = COL_DIM,
    max_lines: int = 2,
) -> int:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if font.size(candidate)[0] <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    for line in lines[:max_lines]:
        _panel_line(surf, font, x, y, line, color)
        y += 16
    return y


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
        BuildKind.LABORATORY: t("build.laboratory"),
        BuildKind.ELECTROLYZER: t("build.electrolyzer"),
        BuildKind.CONDENSER: t("build.condenser"),
    }[kind]


def _draw_build_resources(
    surf: pygame.Surface,
    font_sm: pygame.font.Font,
    rect: pygame.Rect,
    y: int,
    sim: Simulation,
) -> int:
    resources = (
        ("o2", sim.resources.o2, ResourceId.O2),
        ("water", sim.resources.water, ResourceId.WATER),
        ("food", sim.resources.food, ResourceId.FOOD),
        ("power", sim.resources.power, ResourceId.POWER),
        ("mineral", sim.stock.mineral, None),
        ("components", sim.stock.components, None),
    )
    for icon_name, amount, resource in resources:
        color = COL_TEXT
        if resource is not None:
            level = sim.resources.alert_level(resource)
            if level != AlertLevel.OK:
                color = alert_color(level)
        surf.blit(ui_assets.icon(icon_name), (rect.x + 8, y))
        _panel_line(surf, font_sm, rect.x + 28, y, format_amount(amount), color)
        y += 16
    return y


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
    surf.blit(ui_assets.icon("components"), (rect.x + 8, y))
    _panel_line(
        surf,
        font_sm,
        rect.x + 28,
        y,
        t("build.cost", value=format_amount(kind_cost(build.selected))),
    )
    y += 16
    y = _draw_build_resources(surf, font_sm, rect, y, sim)
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
    _panel_wrapped(surf, font_sm, rect.x + 8, y, t("build.hint_place"), rect.w - 16, COL_DIM)


def _draw_module_inspection(
    surf: pygame.Surface,
    font_sm: pygame.font.Font,
    x: int,
    y: int,
    width: int,
    mod,
    world: World,
    sim: Simulation,
) -> int:
    caps = network_caps(world, get_connected(world))
    status = _module_status_key(mod, sim, world, caps)
    _panel_line(
        surf,
        font_sm,
        x,
        y,
        t("panel.status", status=t(status)),
        _status_color(status),
    )
    y += 16
    y = _panel_wrapped(surf, font_sm, x, y, t(f"module_desc.{mod.kind.value}"), width)
    ctx = _module_ctx(sim, world, mod)
    flow = effective_flow(mod, ctx)
    flows = [
        (value, key)
        for field, key in (
            ("o2", "resource.o2"),
            ("power", "resource.power"),
            ("water", "resource.water"),
            ("food", "resource.food"),
            ("mineral", "resource.mineral"),
            ("components", "resource.components"),
        )
        if abs(value := getattr(flow, field)) >= 0.05
    ]
    flows.sort(key=lambda item: item[0] <= 0.0)
    for value, key in flows:
        sign = "+" if value > 0.0 else "-"
        _panel_line(
            surf,
            font_sm,
            x,
            y,
            f"{sign} {t(key)} {abs(value):.1f}/d",
            COL_TEXT if value > 0.0 else COL_DIM,
        )
        y += 16
    radius = module_def(mod.kind).light_radius
    if radius > 0:
        _panel_line(surf, font_sm, x, y, t("panel.light_radius", radius=radius))
        y += 16
    if mod.kind == ModuleKind.STORAGE:
        _panel_line(surf, font_sm, x, y, t("panel.storage_bonus", value=format_amount(STORAGE_NETWORK_BONUS)))
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
    if mod.built_day > 0:
        _panel_line(surf, font_sm, x, y, t("panel.built", day=mod.built_day), COL_DIM)
        y += 16
    if mod.kind == ModuleKind.LABORATORY:
        _panel_line(surf, font_sm, x, y, t("panel.lab_hint"), COL_WARN)
        y += 16
    return y


def _draw_habitat_resources(
    surf: pygame.Surface,
    font_sm: pygame.font.Font,
    rect: pygame.Rect,
    y: int,
    sim: Simulation,
) -> None:
    flow = module_def(ModuleKind.HABITAT).nominal
    vitals = (
        (ResourceId.O2, "o2", flow.o2),
        (ResourceId.WATER, "water", flow.water),
        (ResourceId.FOOD, "food", flow.food),
        (ResourceId.POWER, "power", flow.power),
    )
    _panel_line(surf, font_sm, rect.x + 8, y, t("panel.consumption"), COL_DIM)
    y += 16
    for resource, icon, value in vitals:
        level = sim.resources.alert_level(resource)
        color = COL_TEXT if level == AlertLevel.OK else alert_color(level)
        surf.blit(ui_assets.icon(icon), (rect.x + 8, y))
        _panel_line(surf, font_sm, rect.x + 28, y, f"{value:+.1f}/d", color)
        y += 16

    worst = sim.resources.worst_alert()
    if worst != AlertLevel.OK:
        y += 4
        alert_key = "alert.critical" if worst == AlertLevel.CRITICAL else "alert.warning"
        _panel_line(surf, font_sm, rect.x + 8, y, t(alert_key), alert_color(worst))


def _draw_resource_panel(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
    rect: pygame.Rect,
    sim: Simulation,
    world: World,
) -> None:
    y = rect.y + 10
    surf.blit(font.render(t("panel.resources_title"), False, COL_TEXT), (rect.x + 8, y))
    y += 26

    nc = network_caps(world, get_connected(world))
    resources = (
        ("o2", ResourceId.O2, sim.resources.o2, nc.o2, True),
        ("water", ResourceId.WATER, sim.resources.water, nc.water, True),
        ("food", ResourceId.FOOD, sim.resources.food, nc.food, True),
        ("power", ResourceId.POWER, sim.resources.power, nc.power, True),
        ("mineral", None, sim.stock.mineral, nc.mineral, False),
        ("components", None, sim.stock.components, nc.components, False),
    )
    for icon_name, resource, amount, cap, vital in resources:
        level = sim.resources.alert_level(resource) if resource is not None else None
        color = alert_color(level) if level is not None else COL_DIM
        surf.blit(ui_assets.icon(icon_name), (rect.x + 8, y))
        text = f"{t(f'resource.{icon_name}')} {format_amount(amount)}/{format_amount(cap)}"
        _panel_line(surf, font_sm, rect.x + 28, y, text, color)
        y += 18
        if vital and resource is not None:
            days = sim.resources.days_left(resource)
            _panel_line(
                surf,
                font_sm,
                rect.x + 28,
                y,
                format_days(days),
                alert_color(level) if level is not None else COL_DIM,
            )
            y += 16

    _panel_line(surf, font_sm, rect.x + 8, rect.bottom - 24, t("panel.resources_hint"), COL_DIM)


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
    if layer == MapLayer.RESOURCES:
        _draw_resource_panel(surf, font, font_sm, rect, sim, world)
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
        return

    mod = world.module_at(sel_x, sel_y)
    if mod:
        name = t("module.habitat") if mod.kind == ModuleKind.HABITAT else t(f"module.{mod.kind.value}")
        _panel_line(surf, font_sm, rect.x + 8, y, t("panel.module", name=name))
        y += 18
        if mod.kind == ModuleKind.HABITAT:
            _panel_line(
                surf,
                font_sm,
                rect.x + 8,
                y,
                t("panel.status", status=t("status.life_support")),
            )
            y += 16
            _draw_habitat_resources(surf, font_sm, rect, y, sim)
        else:
            _draw_module_inspection(surf, font_sm, rect.x + 8, y, rect.w - 16, mod, world, sim)
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
