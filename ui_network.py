"""Pantalla de red de la estación de monitoreo."""

from __future__ import annotations

import pygame

from i18n import t
from network_report import NetworkReport, build_network_report, module_count
from resources import RESOURCES, ResourceId, ResourcePool
from simulation import Simulation
from ui_modals import ModalLine, draw_map_modal
from ui_theme import COL_DIM, COL_TEXT, COL_WARN, format_amount
from world import ModuleState, World

NETWORK_VISIBLE_LINES = 12


def _content_lines(report: NetworkReport, resources: ResourcePool) -> list[ModalLine]:
    power = report.balances[ResourceId.POWER]
    lines = [
        ModalLine(
            t(
                "network.power",
                produced=f"{power.produced:.1f}",
                consumed=f"-{power.consumed:.1f}" if power.consumed > 0 else "0.0",
                factor=f"{report.power_factor:.2f}",
            ),
            COL_WARN,
        ),
        ModalLine(
            t(
                "network.modules",
                online=module_count(report, ModuleState.ONLINE),
                offline=module_count(report, ModuleState.OFFLINE),
                building=module_count(report, ModuleState.BUILDING)
                + module_count(report, ModuleState.WAITING),
            ),
            COL_DIM,
        ),
    ]
    for definition in RESOURCES:
        resource = definition.id
        balance = report.balances[resource]
        cap = report.caps[resource]
        lines.append(
            ModalLine(
                t(
                    "network.resource",
                    name=t(definition.name_key),
                    amount=format_amount(resources.amount(resource)),
                    cap=format_amount(cap),
                    produced=f"{balance.produced:.1f}",
                    consumed=f"-{balance.consumed:.1f}" if balance.consumed > 0 else "0.0",
                    net=f"{balance.net:+.1f}",
                ),
                COL_TEXT,
            )
        )
    return lines


def max_network_scroll(world: World, sim: Simulation) -> int:
    report = build_network_report(world, sim)
    return max(0, len(_content_lines(report, sim.resources)) - NETWORK_VISIBLE_LINES)


def draw_network_screen(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
    sim: Simulation,
    world: World,
) -> None:
    report = build_network_report(world, sim)
    content = _content_lines(report, sim.resources)
    start = max(0, min(sim.network_scroll, max(0, len(content) - NETWORK_VISIBLE_LINES)))
    window = content[start : start + NETWORK_VISIBLE_LINES]
    while len(window) < NETWORK_VISIBLE_LINES:
        window.append(ModalLine("", COL_DIM))
    lines = [ModalLine(t("network.title"), COL_TEXT, large=True)] + window
    draw_map_modal(
        surf,
        font,
        font_sm,
        lines,
        dim_map=True,
        footer=[ModalLine(t("network.hint"), COL_DIM)],
    )
