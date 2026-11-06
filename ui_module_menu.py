"""Dibujo del menú contextual A+A de módulos."""

from __future__ import annotations

import pygame

from i18n import t
from module_defs import GENERATOR_FUELS
from simulation import Simulation
from ui_modals import ModalColumn, ModalLine, ModalSpec, draw_modal
from ui_theme import COL_DIM, COL_TEXT, COL_WARN
from world import World


def draw_module_menu(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
    sim: Simulation,
    world: World,
) -> None:
    menu = sim.module_menu
    if menu is None:
        return
    mod = world.module_at(menu.x, menu.y)
    if mod is None:
        return
    lines: list[ModalLine] = []
    if menu.page == "fuel":
        for index, fuel in enumerate(GENERATOR_FUELS):
            selected = index == menu.fuel_index
            current = fuel == mod.fuel_resource
            prefix = ">" if selected else " "
            mark = "[x]" if current else "[ ]"
            color = COL_WARN if selected else COL_TEXT
            name = t(f"resource.{fuel.value}")
            lines.append(ModalLine(f"{prefix} {mark} {name}", color))
        title = t("menu.fuel_title")
        help_text = t("menu.fuel_hint")
    else:
        for index, item in enumerate(menu.items):
            selected = index == menu.index
            prefix = ">" if selected else " "
            if not item.enabled:
                color = COL_DIM
            elif selected:
                color = COL_WARN
            else:
                color = COL_TEXT
            lines.append(ModalLine(f"{prefix} {t(item.label_key)}", color))
        title = t("menu.title", name=t(f"module.{mod.kind.value}"))
        help_text = t("menu.hint")
    spec = ModalSpec(
        title=title,
        columns=(ModalColumn(lines=tuple(lines)),),
        help_text=help_text,
        wide=True,
        dim_map=True,
    )
    draw_modal(surf, font, font_sm, spec)
