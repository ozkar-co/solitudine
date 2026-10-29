"""Tecnologías del slice — datos únicos, sin lógica de UI."""

from __future__ import annotations

from dataclasses import dataclass

from module_kind import ModuleKind


@dataclass(frozen=True)
class TechDef:
    id: str
    name_key: str
    desc_key: str
    branch_key: str
    tier: int
    cost: float
    days: float
    prereqs: tuple[str, ...] = ()
    unlock_kind: ModuleKind | None = None


TECHS: tuple[TechDef, ...] = (
    TechDef(
        id="electrolisis",
        name_key="tech.electrolisis",
        desc_key="tech.electrolisis_desc",
        branch_key="tech.branch.support",
        tier=1,
        cost=4.0,
        days=1.5,
        unlock_kind=ModuleKind.ELECTROLYZER,
    ),
    TechDef(
        id="condensador",
        name_key="tech.condensador",
        desc_key="tech.condensador_desc",
        branch_key="tech.branch.support",
        tier=1,
        cost=4.0,
        days=1.5,
        unlock_kind=ModuleKind.CONDENSER,
    ),
)

TECH_BY_ID = {tech.id: tech for tech in TECHS}


def tech_def(tech_id: str) -> TechDef:
    return TECH_BY_ID[tech_id]


def tech_for_module(kind: ModuleKind) -> str | None:
    for tech in TECHS:
        if tech.unlock_kind == kind:
            return tech.id
    return None
