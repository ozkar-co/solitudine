"""Fachada UI — HUD, modales y re-export de mapa/panel."""

from __future__ import annotations

import pygame

import ui_assets
from config import SCREEN_W
from ui_layout import bottom_bar_rect, top_bar_rect
from construction import BUILD_KINDS, BuildKind, BuildMode, kind_cost
from i18n import t
from resources import AlertLevel, ResourceId
from simulation import Simulation
from ui_map import MapLayer, draw_map
from ui_modals import ModalLine, draw_map_modal
from ui_panel import draw_panel
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
    "draw_dev_debug",
    "draw_game_over",
    "draw_map",
    "draw_panel",
    "draw_pause_modal",
    "draw_top_bar",
    "map_rect",
    "panel_rect",
]


def draw_top_bar(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
    sim: Simulation,
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
    surf.blit(font_sm.render(title, False, COL_TEXT), (8, 1))
    day = f"{t('hud.day', day=sim.day)} {t('hud.hour', hour=sim.hour)}"
    day_s = font_sm.render(day, False, COL_DIM)
    surf.blit(day_s, (SCREEN_W - 8 - day_s.get_width(), 1))

    x = 8
    vitals = (
        ("hud.o2", "o2", ResourceId.O2),
        ("hud.water", "water", ResourceId.WATER),
        ("hud.food", "food", ResourceId.FOOD),
        ("hud.power", "power", ResourceId.POWER),
    )
    for key, icon_name, resource in vitals:
        text = t(key, value=format_amount(sim.resources.amount(resource)))
        level = sim.resources.alert_level(resource)
        stats_s = font_sm.render(text, False, alert_color(level))
        surf.blit(ui_assets.icon(icon_name), (x, 17))
        surf.blit(stats_s, (x + 20, 17))
        x += 20 + stats_s.get_width() + 16

    if worst != AlertLevel.OK:
        alert_key = "alert.critical" if worst == AlertLevel.CRITICAL else "alert.warning"
        alert_s = font_sm.render(t(alert_key), False, alert_color(worst))
        surf.blit(alert_s, (SCREEN_W - 8 - alert_s.get_width(), 17))


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
) -> None:
    from gamepad import format_actions

    rect = map_rect()
    lines = [
        f"FPS {fps:4.1f}  frame {frame_ms:5.1f}ms  tiles {tiles_drawn}  zoom {zoom_px}px",
        f"gen {gen_ms:.0f}ms  held: {format_actions(held)}",
    ]
    y = rect.y + 4
    for line in lines:
        surf.blit(font_sm.render(line, False, (120, 180, 255)), (rect.x + 4, y))
        y += 18
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
    }[kind]


def draw_build_menu_modal(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
    sim: Simulation,
) -> None:
    build = sim.build
    if build.mode != BuildMode.MENU:
        return

    lines: list[ModalLine] = [
        ModalLine(t("build.title"), COL_TEXT, large=True),
        ModalLine(t("build.components", value=format_amount(sim.stock.components)), COL_DIM),
    ]
    for i, kind in enumerate(BUILD_KINDS):
        prefix = ">" if i == build.menu_index else " "
        label = _build_kind_label(kind)
        cost = format_amount(kind_cost(kind))
        color = COL_TEXT if i == build.menu_index else COL_DIM
        lines.append(ModalLine(f"{prefix} {label} ({cost})", color))
    lines.append(ModalLine(t("build.hint_menu"), COL_DIM))
    draw_map_modal(surf, font, font_sm, lines, dim_map=True)


def draw_pause_modal(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
) -> None:
    draw_map_modal(
        surf,
        font,
        font_sm,
        [
            ModalLine(t("pause.title"), COL_TEXT, large=True),
            ModalLine(t("pause.hint"), COL_DIM),
        ],
    )


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
            ModalLine(t("game_over.restart"), COL_DIM),
        ],
        dim_map=True,
    )
