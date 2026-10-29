"""Texto de ayuda contextual según el estado del juego."""

from __future__ import annotations

from construction import BuildController, BuildMode
from i18n import t
from simulation import Simulation


def context_help(
    sim: Simulation,
    build: BuildController,
    *,
    select_x: int | None,
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
    if select_x is not None:
        return t("help.selected")
    return t("help.default")
