"""Dibujo del menú contextual A+A de módulos."""

from __future__ import annotations

import pygame

from i18n import t
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
    spec = ModalSpec(
        title=t("menu.title", name=t(f"module.{mod.kind.value}")),
        columns=(ModalColumn(lines=tuple(lines)),),
        help_text=t("menu.hint"),
        wide=True,
        dim_map=True,
    )
    draw_modal(surf, font, font_sm, spec)
