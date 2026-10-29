"""Texto de ayuda contextual según el estado del juego."""

from __future__ import annotations

from construction import BuildController, BuildMode
from i18n import t
from module_defs import module_def
from simulation import Simulation
from ui_map import MapLayer
from world import World


def context_help(
    sim: Simulation,
    build: BuildController,
    *,
    select_x: int | None,
    select_y: int | None = None,
    world: World | None = None,
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
    if sim.demolish is not None:
        return t("help.demolish_confirm")
    if build.mode == BuildMode.MENU:
        return t("help.build_menu")
    if build.mode == BuildMode.PLACE:
        return t("help.build_place")
    if layer == MapLayer.RESOURCES:
        return t("help.resources")
    if select_x is not None:
        if select_y is not None and world is not None:
            mod = world.module_at(select_x, select_y)
            if mod is not None and not module_def(mod.kind).can_toggle:
                return t("help.selected_fixed")
            if world.has_ruin(select_x, select_y):
                return t("help.ruin")
        return t("help.selected")
    return t("help.default")
