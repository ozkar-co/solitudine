"""Fachada UI — HUD, modales y re-export de mapa/panel."""

from __future__ import annotations

import pygame

import ui_assets
from config import SCREEN_W
from ui_layout import bottom_bar_rect, top_bar_rect
from construction import BUILD_CATEGORIES, BuildKind, BuildMode, kind_cost, kind_locked, module_kind_for
from credits import CREDITS_SECTIONS, CREDITS_VISIBLE_LINES
from i18n import t
from logistics import network_caps
from module_defs import module_def
from network import get_connected
from resources import AlertLevel, ResourceId
from simulation import Simulation
from ui_map import MapLayer, draw_map
from ui_modals import (
    BUILD_MODAL_HEIGHT,
    MODAL_FOOTER_GAP,
    MODAL_PAD_X,
    MODAL_PAD_Y,
    ModalLine,
    draw_map_modal,
)
from ui_panel import draw_panel, module_debug_lines
from ui_theme import (
    COL_BORDER,
    COL_CRITICAL,
    COL_DIM,
    COL_PANEL,
    COL_TEXT,
    COL_WARN,
    alert_color,
    format_amount,
    map_rect,
    panel_rect,
)

__all__ = [
    "MapLayer",
    "draw_bottom_bar",
    "draw_build_menu_modal",
    "draw_credits_modal",
    "draw_easter_egg",
    "draw_dev_debug",
    "draw_game_over",
    "draw_map",
    "draw_mode_badge",
    "draw_panel",
    "draw_pause_modal",
    "draw_splash",
    "module_debug_lines",
    "draw_top_bar",
    "map_rect",
    "panel_rect",
]


def draw_splash(surf: pygame.Surface, title: str, subtitle: str) -> None:
    """Pantalla mínima sin assets para cubrir la carga inicial."""
    w, h = surf.get_size()
    surf.fill((6, 10, 8))
    box = pygame.Rect(0, 0, min(w - 64, 360), 140)
    box.center = (w // 2, h // 2)
    pygame.draw.rect(surf, COL_PANEL, box)
    pygame.draw.rect(surf, COL_BORDER, box, 2)

    font = pygame.font.Font(None, 48)
    font_sm = pygame.font.Font(None, 24)
    title_s = font.render(title, False, COL_TEXT)
    sub_s = font_sm.render(subtitle, False, COL_DIM)
    surf.blit(title_s, (w // 2 - title_s.get_width() // 2, box.y + 28))
    pygame.draw.line(surf, COL_DIM, (box.x + 24, box.y + 80), (box.right - 24, box.y + 80))
    surf.blit(sub_s, (w // 2 - sub_s.get_width() // 2, box.y + 96))
    pygame.display.flip()
    pygame.event.pump()


def draw_top_bar(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
    sim: Simulation,
    world,
) -> None:
    rect = top_bar_rect()
    pygame.draw.rect(surf, COL_PANEL, rect)
    worst = sim.resources.worst_alert()
    bar_border = (
        COL_CRITICAL if worst == AlertLevel.CRITICAL else COL_WARN if worst == AlertLevel.WARNING else COL_BORDER
    )
    pygame.draw.line(surf, bar_border, (0, rect.bottom - 1), (SCREEN_W, rect.bottom - 1))
    if worst != AlertLevel.OK:
        pygame.draw.rect(surf, bar_border, rect, 2)

    title = f"{t('game.title')}  {t('planet.code')}"
    surf.blit(font_sm.render(title, False, COL_TEXT), (8, 0))
    day = f"{t('hud.day', day=sim.day)} {t('hud.hour', hour=sim.hour)}"
    day_s = font_sm.render(day, False, COL_DIM)
    surf.blit(day_s, (SCREEN_W - 8 - day_s.get_width(), 0))

    nc = network_caps(world, get_connected(world))
    x = 8
    vitals = (
        ("o2", t("resource.o2"), sim.resources.o2, nc.o2, ResourceId.O2),
        ("water", t("resource.water"), sim.resources.water, nc.water, ResourceId.WATER),
        ("food", t("resource.food"), sim.resources.food, nc.food, ResourceId.FOOD),
        ("power", t("resource.power"), sim.resources.power, nc.power, ResourceId.POWER),
    )
    for icon_name, label, amount, cap, resource in vitals:
        text = f"{label} {format_amount(amount)}/{format_amount(cap)}"
        level = sim.resources.alert_level(resource)
        color = COL_TEXT if level == AlertLevel.OK else alert_color(level)
        stats_s = font_sm.render(text, False, color)
        surf.blit(ui_assets.icon(icon_name), (x, 16))
        surf.blit(stats_s, (x + 20, 16))
        x += 20 + stats_s.get_width() + 8


def draw_mode_badge(
    surf: pygame.Surface,
    font_sm: pygame.font.Font,
    sim: Simulation,
    build,
    layer: MapLayer,
) -> None:
    if sim.credits_open or sim.easter_egg_open:
        return
    label = None
    color = COL_TEXT
    if sim.user_paused:
        label = t("mode.paused")
        color = COL_WARN
    elif build.mode == BuildMode.PLACE:
        label = f"{t('mode.place')} · {t('mode.paused')}"
        color = COL_WARN
    elif build.mode == BuildMode.MENU:
        label = f"{t('mode.build')} · {t('mode.paused')}"
        color = COL_WARN
    elif layer == MapLayer.RESOURCES:
        label = t("mode.resources")
    if label is None:
        return
    text = font_sm.render(label, False, color)
    rect = map_rect()
    badge = pygame.Rect(rect.x + 8, rect.y + 8, text.get_width() + 12, text.get_height() + 6)
    pygame.draw.rect(surf, COL_PANEL, badge)
    pygame.draw.rect(surf, COL_BORDER, badge, 1)
    surf.blit(text, (badge.x + 6, badge.y + 3))


def draw_bottom_bar(surf: pygame.Surface, font_sm: pygame.font.Font, text: str) -> None:
    rect = bottom_bar_rect()
    pygame.draw.rect(surf, COL_PANEL, rect)
    pygame.draw.line(surf, COL_BORDER, (0, rect.y), (SCREEN_W, rect.y))
    surf.blit(font_sm.render(text, False, COL_DIM), (8, rect.y + 8))


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
    zoom_px: int,
    debug_lines: list[str] | None = None,
) -> None:
    from gamepad import format_actions

    rect = map_rect()
    lines = [
        f"FPS {fps:4.1f}  frame {frame_ms:5.1f}ms  celdas {tiles_drawn}  zoom {zoom_px}px",
        f"gen {gen_ms:.0f}ms  held: {format_actions(held)}",
    ]
    y = rect.y + 4
    for line in lines:
        surf.blit(font_sm.render(line, False, (120, 180, 255)), (rect.x + 4, y))
        y += 18
    if debug_lines:
        y += 4
        surf.blit(font_sm.render("DEBUG módulo (nominal)", False, (120, 180, 255)), (rect.x + 4, y))
        y += 16
        for line in debug_lines:
            surf.blit(font_sm.render(line, False, (90, 140, 200)), (rect.x + 4, y))
            y += 16
    y += 4
    for line in keymap.splitlines():
        surf.blit(font_sm.render(line, False, (90, 140, 200)), (rect.x + 4, y))
        y += 16


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


def _build_kind_desc(kind: BuildKind) -> str:
    if kind == BuildKind.CABLE:
        return t("module_desc.cable")
    return t(f"module_desc.{module_kind_for(kind).value}")


_BUILD_FLOW_FIELDS = (
    ("o2", "o2"),
    ("water", "water"),
    ("food", "food"),
    ("power", "power"),
    ("mineral", "mineral"),
    ("components", "components"),
)


def _build_effect_line(
    kind: BuildKind,
    production_color: tuple[int, int, int],
) -> ModalLine:
    if kind == BuildKind.CABLE:
        return ModalLine(t("build.no_flow"), COL_DIM)
    defn = module_def(module_kind_for(kind))
    if kind == BuildKind.STORAGE:
        return ModalLine(
            t("build.cap_bonus", value=format_amount(defn.storage_cap_bonus)),
            COL_DIM,
        )

    flow = defn.nominal
    producers: list[tuple[str, str, tuple[int, int, int]]] = []
    consumers: list[tuple[str, str, tuple[int, int, int]]] = []
    for field, icon in _BUILD_FLOW_FIELDS:
        value = getattr(flow, field)
        if value > 0.0:
            producers.append((icon, f"+{value:.1f}", production_color))
        elif value < 0.0:
            consumers.append((icon, f"{value:.1f}", COL_DIM))
    if not producers and not consumers:
        return ModalLine(t("build.no_flow"), COL_DIM)

    items = []
    if producers:
        items.append(("", f"{t('build.produces')} ", COL_DIM))
        items.extend(producers)
    if consumers:
        prefix = "  " if producers else ""
        items.append(("", f"{prefix}{t('build.consumes')} ", COL_DIM))
        items.extend(consumers)
    return ModalLine(items=tuple(items), item_gap=8)


def _resource_modal_lines(sim: Simulation) -> list[ModalLine]:
    resources = (
        ("o2", sim.resources.o2, ResourceId.O2),
        ("water", sim.resources.water, ResourceId.WATER),
        ("food", sim.resources.food, ResourceId.FOOD),
        ("power", sim.resources.power, ResourceId.POWER),
        ("mineral", sim.stock.mineral, None),
        ("components", sim.stock.components, None),
    )
    items: list[tuple[str, str, tuple[int, int, int]]] = []
    for icon_name, amount, resource in resources:
        color = COL_TEXT
        if resource is not None:
            level = sim.resources.alert_level(resource)
            if level != AlertLevel.OK:
                color = alert_color(level)
        items.append((icon_name, format_amount(amount), color))
    return [ModalLine(items=tuple(items[:3])), ModalLine(items=tuple(items[3:]))]


def _category_segments(build) -> tuple[tuple[str, tuple[int, int, int]], ...]:
    segments: list[tuple[str, tuple[int, int, int]]] = []
    for index, (category_key, _kinds) in enumerate(BUILD_CATEGORIES):
        label = t(category_key)
        if index == build.menu_category:
            segments.append((f"< {label} >", COL_WARN))
        else:
            segments.append((f"  {label}  ", COL_DIM))
    return tuple(segments)


def draw_build_menu_modal(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
    sim: Simulation,
    world,
) -> None:
    build = sim.build
    if build.mode != BuildMode.MENU:
        return

    lines: list[ModalLine] = [
        ModalLine(t("build.title"), COL_TEXT, large=True),
        *_resource_modal_lines(sim),
        ModalLine(segments=_category_segments(build)),
    ]

    _category_key, kinds = BUILD_CATEGORIES[build.menu_category]
    for kind in kinds:
        selected = kind == build.selected
        prefix = ">" if selected else " "
        cost = kind_cost(kind)
        locked = kind_locked(kind, sim.research.unlocked)
        affordable = sim.stock.can_afford(cost)
        suffix = ""
        if locked:
            suffix = f"  {t('build.locked')}"
        elif not affordable:
            suffix = f"  {t('build.missing', value=format_amount(cost - sim.stock.components))}"
        unavailable = locked or not affordable
        if unavailable:
            color = COL_WARN if selected else COL_DIM
        else:
            color = COL_TEXT
        items = [
            ("", f"{prefix} {_build_kind_label(kind)} ( ", color),
            ("components", f"{format_amount(cost)})", color),
        ]
        if suffix:
            items.append(("", suffix, color))
        lines.append(ModalLine(items=tuple(items), item_gap=0))
        lines.append(ModalLine(_build_kind_desc(kind), COL_DIM))
        lines.append(_build_effect_line(kind, COL_DIM if unavailable else COL_TEXT))
    draw_map_modal(
        surf,
        font,
        font_sm,
        lines,
        dim_map=True,
        min_width=608,
        fixed_height=BUILD_MODAL_HEIGHT,
        footer=[ModalLine(t("build.hint_menu"), COL_DIM)],
        wide=True,
    )


def draw_pause_modal(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
    sim: Simulation,
) -> None:
    options = (t("pause.menu_continue"), t("pause.menu_credits"))
    lines = [ModalLine(t("pause.title"), COL_TEXT, large=True)]
    for index, label in enumerate(options):
        selected = index == sim.pause_index
        prefix = ">" if selected else " "
        lines.append(ModalLine(f"{prefix} {label}", COL_TEXT if selected else COL_DIM))
    draw_map_modal(
        surf,
        font,
        font_sm,
        lines,
        dim_map=True,
        footer=[ModalLine(t("pause.hint_menu"), COL_DIM)],
    )


def _credits_content() -> list[ModalLine]:
    lines: list[ModalLine] = []
    for section_key, entries in CREDITS_SECTIONS:
        lines.append(ModalLine(t(section_key), COL_WARN))
        for entry in entries:
            lines.append(ModalLine(t(entry.name_key), COL_TEXT))
            lines.append(ModalLine(t(entry.role_key), COL_DIM))
    return lines


def draw_credits_modal(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
    sim: Simulation,
) -> None:
    content = _credits_content()
    max_scroll = max(0, len(content) - CREDITS_VISIBLE_LINES)
    scroll = min(max(sim.credits_scroll, 0), max_scroll)
    window = content[scroll : scroll + CREDITS_VISIBLE_LINES]
    window += [ModalLine("", COL_DIM)] * (CREDITS_VISIBLE_LINES - len(window))

    title = ModalLine(t("credits.title"), COL_TEXT, large=True)
    lines = [title] + window

    title_h = font.get_height() + 4
    line_h = font_sm.get_height() + 2
    footer_h = font_sm.get_height() + 2
    fixed_height = (
        MODAL_PAD_Y * 2
        + title_h
        + CREDITS_VISIBLE_LINES * line_h
        + footer_h
        + MODAL_FOOTER_GAP
    )
    min_width = (
        max(
            font.render(title.text, False, title.color).get_width(),
            *(font_sm.render(line.text, False, line.color).get_width() for line in content),
        )
        + MODAL_PAD_X * 2
        + 8
    )
    box = draw_map_modal(
        surf,
        font,
        font_sm,
        lines,
        dim_map=True,
        min_width=min_width,
        fixed_height=fixed_height,
        footer=[ModalLine(t("help.credits"), COL_DIM)],
    )

    if max_scroll > 0:
        track_x = box.right - 8
        track_top = box.y + MODAL_PAD_Y + title_h + 2
        track_bottom = box.bottom - MODAL_PAD_Y - footer_h - MODAL_FOOTER_GAP + 2
        track_h = max(1, track_bottom - track_top)
        pygame.draw.rect(surf, COL_DIM, (track_x, track_top, 2, track_h))
        thumb_h = max(8, int(track_h * CREDITS_VISIBLE_LINES / len(content)))
        thumb_y = track_top + int((track_h - thumb_h) * scroll / max_scroll)
        pygame.draw.rect(surf, COL_TEXT, (track_x, thumb_y, 2, thumb_h))


def draw_easter_egg(surf: pygame.Surface) -> None:
    image = ui_assets.easter_egg()
    if image is None:
        return
    if image.get_size() != surf.get_size():
        image = pygame.transform.scale(image, surf.get_size())
    surf.blit(image, (0, 0))


def draw_game_over(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
    sim: Simulation,
) -> None:
    draw_map_modal(
        surf,
        font,
        font_sm,
        [
            ModalLine(t("game_over.title"), COL_CRITICAL, large=True),
            ModalLine(t(sim.death_cause), COL_TEXT),
        ],
        dim_map=True,
        footer=[ModalLine(t("game_over.restart"), COL_DIM)],
    )
