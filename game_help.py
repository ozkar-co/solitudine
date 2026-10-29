"""Texto de ayuda contextual según el estado del juego."""

from __future__ import annotations

from construction import BuildController, BuildMode
from i18n import t
from simulation import Simulation
from ui_map import MapLayer


def context_help(
    sim: Simulation,
    build: BuildController,
    *,
    select_x: int | None,
    layer: MapLayer,
) -> str:
    if sim.game_over:
        return t("help.game_over")
    if sim.research.open:
        return t("help.tech")
    if sim.credits_open:
        return t("help.credits")
    if sim.user_paused:
        return t("help.paused")
    if build.mode == BuildMode.MENU:
        return t("help.build_menu")
    if build.mode == BuildMode.PLACE:
        return t("help.build_place")
    if layer == MapLayer.RESOURCES:
        return t("help.resources")
    if select_x is not None:
        return t("help.selected")
    return t("help.default")
