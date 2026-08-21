"""Fachada UI — HUD, modales y re-export de mapa/panel."""

from __future__ import annotations

import pygame

from config import BOTTOM_BAR_H, SCREEN_H, SCREEN_W, TOP_BAR_H
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
    mat_s = font_sm.render(t("hud.components", value=format_amount(sim.stock.components)), True, COL_DIM)
    stats_x -= mat_s.get_width() + 10
    surf.blit(mat_s, (stats_x, 9))

    o2 = format_amount(sim.resources.o2)
    power = format_amount(sim.resources.power)
    for text, level in (
        (t("hud.power", value=power), sim.resources.alert_level(ResourceId.POWER)),
        (t("hud.o2", value=o2), sim.resources.alert_level(ResourceId.O2)),
    ):
        stats_s = font_sm.render(text, True, alert_color(level))
        stats_x -= stats_s.get_width() + 10
        surf.blit(stats_s, (stats_x, 9))


def draw_bottom_bar(surf: pygame.Surface, font_sm: pygame.font.Font, text: str) -> None:
    y = SCREEN_H - BOTTOM_BAR_H
    pygame.draw.rect(surf, COL_PANEL, (0, y, SCREEN_W, BOTTOM_BAR_H))
    pygame.draw.line(surf, COL_BORDER, (0, y), (SCREEN_W, y))
    surf.blit(font_sm.render(text, True, COL_DIM), (8, y + 5))


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
