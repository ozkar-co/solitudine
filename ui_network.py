"""Pantalla de red de la estación de monitoreo."""

from __future__ import annotations

import pygame

from i18n import t
from network_report import NetworkReport, build_network_report, module_count
from resources import RESOURCES
from simulation import Simulation
from ui_modals import ModalColumn, ModalLine, ModalSpec, draw_modal
from ui_theme import COL_DIM, COL_TEXT, COL_WARN
from world import ModuleState, World

NETWORK_VISIBLE_LINES = 12


def _columns(report: NetworkReport) -> tuple[ModalColumn, ModalColumn]:
    production: list[ModalLine] = []
    consumption: list[ModalLine] = []
    for definition in RESOURCES:
        balance = report.balances[definition.id]
        if balance.produced > 0.0:
            production.append(
                ModalLine(
                    items=(
                        (
                            definition.icon,
                            f"{t(definition.name_key)} +{balance.produced:.1f}/d",
                            COL_TEXT,
                        ),
                    )
                )
            )
        if balance.consumed > 0.0:
            consumption.append(
                ModalLine(
                    items=(
                        (
                            definition.icon,
                            f"{t(definition.name_key)} -{balance.consumed:.1f}/d",
                            COL_WARN,
                        ),
                    )
                )
            )
    if not production:
        production.append(ModalLine(t("network.empty"), COL_DIM))
    if not consumption:
        consumption.append(ModalLine(t("network.empty"), COL_DIM))
    return (
        ModalColumn(header=t("network.production"), lines=tuple(production), align="left"),
        ModalColumn(header=t("network.consumption"), lines=tuple(consumption), align="left"),
    )


def max_network_scroll(world: World, sim: Simulation) -> int:
    report = build_network_report(world, sim)
    columns = _columns(report)
    longest = max(len(column.lines) for column in columns)
    return max(0, longest - NETWORK_VISIBLE_LINES)


def draw_network_screen(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
    sim: Simulation,
    world: World,
) -> None:
    report = build_network_report(world, sim)
    subtitle = t(
        "network.modules",
        online=module_count(report, ModuleState.ONLINE),
        offline=module_count(report, ModuleState.OFFLINE),
        building=module_count(report, ModuleState.BUILDING)
        + module_count(report, ModuleState.WAITING),
    )
    spec = ModalSpec(
        title=t("network.title"),
        subtitle=subtitle,
        columns=_columns(report),
        help_text=t("network.hint"),
        wide=True,
        visible_lines=NETWORK_VISIBLE_LINES,
        fill_height=True,
        dim_map=True,
    )
    draw_modal(surf, font, font_sm, spec, scroll=sim.network_scroll)
