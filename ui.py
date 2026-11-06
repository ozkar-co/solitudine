"""Fachada UI — HUD, modales y re-export de mapa/panel."""

from __future__ import annotations

import math

import pygame

import demolition
import ui_assets
from config import (
    BUILD_MENU_VISIBLE_CARDS,
    FUEL_GENERATOR_BIODIESEL_POWER_DAILY,
    FUEL_GENERATOR_WOOD_POWER_DAILY,
    SCREEN_W,
)
from ui_layout import bottom_bar_rect, top_bar_rect
from construction import BUILD_CATEGORIES, BuildKind, BuildMode, kind_cost, kind_locked, module_kind_for
from credits import CREDITS_SECTIONS, CREDITS_VISIBLE_LINES
from i18n import t
from logistics import network_caps
from module_defs import CABLE_COST, ModuleKind, module_def
from network import get_connected
from resources import (
    RESOURCE_BY_ID,
    RESOURCES,
    TOPBAR_IDS,
    AlertLevel,
    Cost,
    ResourceId,
)
from simulation import Simulation
from ui_map import MapLayer, draw_map
from ui_modals import (
    BUILD_CARD_GAP,
    BUILD_CARD_HEIGHT,
    BUILD_CARD_ICON,
    MODAL_PAD_X,
    ModalColumn,
    ModalLine,
    ModalSpec,
    draw_modal,
    draw_scrollbar,
    render_items,
    render_segments,
)
from ui_panel import build_kind_label, draw_panel, module_debug_lines
from ui_theme import (
    COL_BORDER,
    COL_CARD,
    COL_CARD_BORDER,
    COL_CARD_SELECTED,
    COL_CRITICAL,
    COL_DIM,
    COL_PANEL,
    COL_TEXT,
    COL_WARN,
    alert_color,
    format_amount,
    format_cost_text,
    map_rect,
    panel_rect,
)

__all__ = [
    "MapLayer",
    "draw_bottom_bar",
    "draw_build_menu_modal",
    "draw_credits_modal",
    "draw_demolish_modal",
    "draw_easter_egg",
    "draw_dev_debug",
    "draw_game_over",
    "draw_map",
    "draw_mode_badge",
    "draw_panel",
    "draw_pause_modal",
    "draw_new_game_modal",
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

    font = ui_assets.load_font(ui_assets.FONT_TITLE_FILE, 48)
    font_sm = ui_assets.load_font(ui_assets.FONT_BODY_FILE, 24)
    title_s = font.render(title, False, COL_TEXT)
    sub_s = font_sm.render(subtitle, False, COL_DIM)
    surf.blit(title_s, (w // 2 - title_s.get_width() // 2, box.y + 28))
    pygame.draw.line(surf, COL_DIM, (box.x + 24, box.y + 80), (box.right - 24, box.y + 80))
    surf.blit(sub_s, (w // 2 - sub_s.get_width() // 2, box.y + 96))
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

    title = f"{t('game.title')}  {world.seed}"
    surf.blit(font_sm.render(title, False, COL_TEXT), (8, 0))
    day = f"{t('hud.day', day=sim.day)} {t('hud.hour', hour=sim.hour)}"
    day_s = font_sm.render(day, False, COL_DIM)
    surf.blit(day_s, (SCREEN_W - 8 - day_s.get_width(), 0))

    nc = network_caps(world, get_connected(world))
    x = 8
    for resource in TOPBAR_IDS:
        defn = RESOURCE_BY_ID[resource]
        amount = sim.resources.amount(resource)
        cap = nc[resource]
        text = f"{t(defn.name_key)} {format_amount(amount)}/{format_amount(cap)}"
        level = sim.resources.alert_level(resource)
        color = COL_TEXT if level == AlertLevel.OK else alert_color(level)
        stats_s = font_sm.render(text, False, color)
        surf.blit(ui_assets.icon(defn.icon), (x, 16))
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
    time_scale: float = 1.0,
    debug_lines: list[str] | None = None,
) -> None:
    from gamepad import format_actions

    rect = map_rect()
    lines = [
        f"FPS {fps:4.1f}  frame {frame_ms:5.1f}ms  celdas {tiles_drawn}  zoom {zoom_px}px  tiempo x{time_scale:g}",
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
    ("scrap", "scrap"),
    ("wood", "wood"),
    ("coal", "coal"),
    ("fuel", "fuel"),
    ("crystal", "crystal"),
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
    if kind == BuildKind.BATTERY:
        resource, amount = next(iter(defn.storage_caps.items()))
        return ModalLine(
            t(
                "build.cap_resource",
                resource=t(f"resource.{resource.value}"),
                value=format_amount(amount),
            ),
            COL_DIM,
        )
    if kind == BuildKind.FUEL_GENERATOR:
        return ModalLine(
            t(
                "build.generator_output",
                low=format_amount(FUEL_GENERATOR_WOOD_POWER_DAILY),
                high=format_amount(FUEL_GENERATOR_BIODIESEL_POWER_DAILY),
            ),
            COL_DIM,
        )
    if kind == BuildKind.FISH_TRAP:
        return ModalLine(
            t("build.fish_trap_output", value=format_amount(defn.nominal.food)),
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
    items: list[tuple[str, str, tuple[int, int, int]]] = []
    for defn in RESOURCES:
        color = COL_TEXT
        if defn.alert:
            level = sim.resources.alert_level(defn.id)
            if level != AlertLevel.OK:
                color = alert_color(level)
        items.append((defn.icon, format_amount(sim.resources.amount(defn.id)), color))
    return [ModalLine(items=tuple(items[i : i + 4])) for i in range(0, len(items), 4)]


def _draw_category_carousel(
    surf: pygame.Surface,
    font_sm: pygame.font.Font,
    box: pygame.Rect,
    y: int,
    build,
) -> None:
    count = len(BUILD_CATEGORIES)
    spacing = (box.w - MODAL_PAD_X * 2) / 5.0
    for offset in range(-2, 3):
        idx_float = build.category_visual + offset
        idx = int(round(idx_float)) % count
        pos = idx_float - build.category_visual
        selected = idx == build.menu_category
        label = t(BUILD_CATEGORIES[idx][0])
        text = f"< {label} >" if selected else label
        color = COL_WARN if selected else COL_DIM
        alpha = 255 if selected else max(55, int(255 * (1.0 - min(1.0, abs(pos)) * 0.55)))
        rendered = font_sm.render(text, False, color)
        rendered.set_alpha(alpha)
        x = int(box.centerx + pos * spacing - rendered.get_width() / 2)
        surf.blit(rendered, (x, y))


_BUILD_ICON_CACHE: dict[BuildKind, pygame.Surface] = {}


def _build_icon(kind: BuildKind) -> pygame.Surface:
    cached = _BUILD_ICON_CACHE.get(kind)
    if cached is not None:
        return cached
    if kind == BuildKind.CABLE:
        icon = pygame.transform.scale(
            ui_assets.icon("cable"), (BUILD_CARD_ICON, BUILD_CARD_ICON)
        )
    else:
        icon = ui_assets.module(module_kind_for(kind), BUILD_CARD_ICON)
    _BUILD_ICON_CACHE[kind] = icon
    return icon


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

    frame = draw_modal(
        surf,
        font,
        font_sm,
        ModalSpec(
            title=t("build.title"),
            help_text=t("build.hint_menu"),
            wide=True,
            fill_height=True,
            dim_map=True,
        ),
    )
    box = frame.box
    y = frame.content.y

    for line in _resource_modal_lines(sim):
        row = render_items(line.items, font_sm, line.item_gap)
        surf.blit(row, (box.centerx - row.get_width() // 2, y))
        y += row.get_height() + 2

    _draw_category_carousel(surf, font_sm, box, y, build)
    y += font_sm.get_height() + 8
    pygame.draw.line(
        surf,
        COL_DIM,
        (box.x + MODAL_PAD_X, y),
        (box.right - MODAL_PAD_X, y),
    )
    y += 6

    _category_key, kinds = BUILD_CATEGORIES[build.menu_category]
    card_x = box.x + MODAL_PAD_X
    card_w = box.w - MODAL_PAD_X * 2
    step = BUILD_CARD_HEIGHT + BUILD_CARD_GAP
    content_top = y
    content_bottom = frame.content.bottom
    clip = pygame.Rect(
        card_x,
        content_top,
        card_w,
        max(0, content_bottom - content_top),
    )
    prev_clip = surf.get_clip()
    surf.set_clip(clip)
    start = max(0, int(math.floor(build.menu_scroll)) - 1)
    end = min(
        len(kinds),
        int(math.ceil(build.menu_scroll)) + BUILD_MENU_VISIBLE_CARDS + 1,
    )
    for index in range(start, end):
        kind = kinds[index]
        card_y = content_top + (index - build.menu_scroll) * step
        card = pygame.Rect(card_x, round(card_y), card_w, BUILD_CARD_HEIGHT)
        selected = kind == build.selected
        cost = kind_cost(kind)
        locked = kind_locked(kind, sim.research.unlocked)
        affordable = cost.can_afford(sim.resources)
        missing = cost.missing(sim.resources)
        unavailable = locked or not affordable
        color = (COL_WARN if selected else COL_DIM) if unavailable else COL_TEXT

        pygame.draw.rect(
            surf, COL_CARD_SELECTED if selected else COL_CARD, card
        )
        pygame.draw.rect(
            surf,
            COL_WARN if selected else COL_CARD_BORDER,
            card,
            2 if selected else 1,
        )
        if selected:
            pygame.draw.rect(
                surf, COL_WARN, (card.x + 2, card.y + 8, 3, card.h - 16)
            )

        icon = _build_icon(kind)
        surf.blit(
            icon,
            (card.x + 9, card.y + (card.h - icon.get_height()) // 2),
        )
        text_x = card.x + 9 + BUILD_CARD_ICON + 10
        text_y = card.y + 5

        items = [("", f"{build_kind_label(kind)} ( ", color)]
        for resource, amount in cost.items():
            items.append(
                (RESOURCE_BY_ID[resource].icon, format_amount(amount), color)
            )
        items.append(("", ")", color))
        name_row = render_items(tuple(items), font_sm, 4)
        surf.blit(name_row, (text_x, text_y))

        status = ""
        if locked:
            status = t("build.locked")
        elif missing:
            status = t("build.missing", value=format_cost_text(Cost(missing)))
        if status:
            status_color = COL_WARN if selected else COL_DIM
            status_s = font_sm.render(status, False, status_color)
            status_x = card.right - 9 - status_s.get_width()
            if status_x > text_x + name_row.get_width() + 8:
                surf.blit(status_s, (status_x, text_y))
            else:
                surf.blit(
                    status_s,
                    (card.right - 9 - status_s.get_width(), card.bottom - 18),
                )

        desc = font_sm.render(_build_kind_desc(kind), False, COL_DIM)
        surf.blit(desc, (text_x, text_y + 16))
        effect = _build_effect_line(kind, color)
        if effect.items:
            effect_row = render_items(effect.items, font_sm, effect.item_gap)
        else:
            effect_row = font_sm.render(effect.text, False, effect.color)
        surf.blit(effect_row, (text_x, text_y + 32))

    surf.set_clip(prev_clip)

    if len(kinds) > BUILD_MENU_VISIBLE_CARDS:
        draw_scrollbar(
            surf,
            box.right - 8,
            content_top,
            max(1, content_bottom - content_top),
            BUILD_MENU_VISIBLE_CARDS,
            len(kinds),
            build.menu_scroll,
        )



def draw_demolish_modal(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
    sim: Simulation,
    world,
) -> None:
    if sim.demolish is None:
        return
    x, y = sim.demolish
    mod = world.module_at(x, y)
    lines: list[ModalLine] = []
    if mod is not None:
        if mod.kind == ModuleKind.HABITAT:
            return
        name = t(f"module.{mod.kind.value}")
        if demolition.is_site(mod):
            lines.append(ModalLine(t("demolish.site", name=name), COL_TEXT))
            lines.append(
                ModalLine(
                    t("demolish.scrap", value=format_amount(demolition.cancel_scrap(mod))),
                    COL_WARN,
                )
            )
            lines.append(ModalLine(t("demolish.cancel_warning"), COL_DIM))
        else:
            lines.append(ModalLine(t("demolish.module", name=name), COL_TEXT))
            low, high = demolition.scrap_range(mod)
            lines.append(
                ModalLine(
                    t(
                        "demolish.scrap_range",
                        low=format_amount(low),
                        high=format_amount(high),
                    ),
                    COL_WARN,
                )
            )
            lines.append(ModalLine(t("demolish.ruin_warning"), COL_DIM))
    elif (x, y) in world.cables:
        lines.append(ModalLine(t("demolish.cable"), COL_TEXT))
        refund = CABLE_COST.amounts.get(ResourceId.COMPONENTS, 0.0)
        lines.append(ModalLine(t("demolish.components", value=format_amount(refund)), COL_WARN))
    else:
        return
    spec = ModalSpec(
        title=t("demolish.title"),
        subtitle=t("panel.coords", x=x, y=y),
        columns=(ModalColumn(lines=tuple(lines)),),
        help_text=t("demolish.hint"),
        wide=True,
        dim_map=True,
    )
    draw_modal(surf, font, font_sm, spec)


def draw_pause_modal(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
    sim: Simulation,
) -> None:
    options = (
        t("pause.menu_continue"),
        t("pause.menu_credits"),
        t("pause.menu_new_game"),
        t("pause.menu_exit"),
    )
    lines: list[ModalLine] = []
    for index, label in enumerate(options):
        selected = index == sim.pause_index
        prefix = ">" if selected else " "
        lines.append(ModalLine(f"{prefix} {label}", COL_TEXT if selected else COL_DIM))
    spec = ModalSpec(
        title=t("pause.title"),
        columns=(ModalColumn(lines=tuple(lines)),),
        help_text=t("pause.hint_menu"),
        wide=True,
        dim_map=True,
    )
    draw_modal(surf, font, font_sm, spec)


def draw_new_game_modal(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
) -> None:
    spec = ModalSpec(
        title=t("new_game.title"),
        columns=(
            ModalColumn(
                lines=(
                    ModalLine(t("new_game.warning"), COL_WARN),
                    ModalLine(t("new_game.info"), COL_TEXT),
                )
            ),
        ),
        help_text=t("new_game.hint"),
        wide=True,
        dim_map=True,
    )
    draw_modal(surf, font, font_sm, spec)


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
    spec = ModalSpec(
        title=t("credits.title"),
        columns=(ModalColumn(lines=tuple(content)),),
        help_text=t("help.credits"),
        wide=True,
        visible_lines=CREDITS_VISIBLE_LINES,
        fill_height=True,
        dim_map=True,
    )
    draw_modal(surf, font, font_sm, spec, scroll=sim.credits_scroll)


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
    spec = ModalSpec(
        title=t("game_over.title"),
        title_color=COL_CRITICAL,
        columns=(ModalColumn(lines=(ModalLine(t(sim.death_cause), COL_TEXT),)),),
        help_text=t("game_over.restart"),
        wide=True,
        dim_map=True,
    )
    draw_modal(surf, font, font_sm, spec)
