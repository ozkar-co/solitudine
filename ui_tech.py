"""Pantalla mínima de Tecnología."""

from __future__ import annotations

import pygame

from i18n import t
from research import has_active_lab
from simulation import Simulation
from tech_defs import TECHS, tech_def
from ui_modals import MODAL_HEIGHT, ModalLine, draw_map_modal
from ui_theme import COL_CABLE, COL_DIM, COL_TEXT, COL_WARN
from world import World


def draw_tech_screen(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
    sim: Simulation,
    world: World,
) -> None:
    research = sim.research
    selected = research.selected_tech()
    lines: list[ModalLine] = [ModalLine(t("tech.title"), COL_TEXT, large=True)]

    for tech in TECHS:
        is_selected = tech.id == selected.id
        prefix = ">" if is_selected else " "
        if tech.id in research.unlocked:
            status = t("tech.status.unlocked")
            color = COL_CABLE
        elif research.active == tech.id:
            status = t("tech.status.active")
            color = COL_WARN
        else:
            status = t("tech.status.locked")
            color = COL_TEXT if is_selected else COL_DIM
        text = f"{prefix} {status} {t(tech.name_key)}  T{tech.tier}  {tech.cost:.0f} Cmp / {tech.days:.0f}d"
        lines.append(ModalLine(text, color))

    lines.append(ModalLine(t(selected.desc_key), COL_DIM))
    if selected.unlock_kind is not None:
        lines.append(ModalLine(t("tech.unlocks", name=t(f"build.{selected.unlock_kind.value}")), COL_DIM))
    requires = ", ".join(t(tech_def(p).name_key) for p in selected.prereqs) if selected.prereqs else t("tech.lab")
    lines.append(ModalLine(t("tech.requires", value=requires), COL_DIM))
    if research.active == selected.id:
        lines.append(ModalLine(t("tech.progress", value=f"{research.progress:.2f}", total=f"{selected.days:.0f}"), COL_WARN))
    elif research.active is not None:
        lines.append(ModalLine(t("tech.busy", name=t(tech_def(research.active).name_key)), COL_WARN))
    if selected.id in research.unlocked:
        lines.append(ModalLine(t("tech.done"), COL_CABLE))
    elif not has_active_lab(world):
        lines.append(ModalLine(t("tech.no_lab"), COL_WARN))
    elif sim.resources.power <= 0.0:
        lines.append(ModalLine(t("tech.no_power"), COL_WARN))
    draw_map_modal(
        surf,
        font,
        font_sm,
        lines,
        dim_map=True,
        fixed_height=MODAL_HEIGHT,
        footer=[ModalLine(t("tech.hint"), COL_DIM)],
    )

