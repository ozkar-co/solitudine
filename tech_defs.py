"""Tecnologías del slice — datos únicos, sin lógica de UI."""

from __future__ import annotations

from dataclasses import dataclass

from config import (
    COST_TECH_ALMACENAMIENTO,
    COST_TECH_CARBON,
    COST_TECH_CONDENSADOR,
    COST_TECH_CRISTALOGRAFIA,
    COST_TECH_ELECTROLISIS,
    COST_TECH_FOTOVOLTAICA,
    COST_TECH_RECICLAJE,
)
from module_kind import ModuleKind
from resources import Cost


@dataclass(frozen=True)
class TechDef:
    id: str
    name_key: str
    desc_key: str
    branch_key: str
    tier: int
    cost: Cost
    days: float
    prereqs: tuple[str, ...] = ()
    unlock_kinds: tuple[ModuleKind, ...] = ()


TECHS: tuple[TechDef, ...] = (
    TechDef(
        id="fotovoltaica",
        name_key="tech.fotovoltaica",
        desc_key="tech.fotovoltaica_desc",
        branch_key="tech.branch.energy",
        tier=1,
        cost=Cost(COST_TECH_FOTOVOLTAICA),
        days=0.5,
        unlock_kinds=(ModuleKind.SOLAR,),
    ),
    TechDef(
        id="carbon",
        name_key="tech.carbon",
        desc_key="tech.carbon_desc",
        branch_key="tech.branch.extraction",
        tier=1,
        cost=Cost(COST_TECH_CARBON),
        days=0.75,
        unlock_kinds=(ModuleKind.COAL_EXTRACTOR,),
    ),
    TechDef(
        id="electrolisis",
        name_key="tech.electrolisis",
        desc_key="tech.electrolisis_desc",
        branch_key="tech.branch.support",
        tier=1,
        cost=Cost(COST_TECH_ELECTROLISIS),
        days=1.5,
        unlock_kinds=(ModuleKind.ELECTROLYZER,),
    ),
    TechDef(
        id="condensador",
        name_key="tech.condensador",
        desc_key="tech.condensador_desc",
        branch_key="tech.branch.support",
        tier=1,
        cost=Cost(COST_TECH_CONDENSADOR),
        days=1.5,
        unlock_kinds=(ModuleKind.CONDENSER,),
    ),
    TechDef(
        id="reciclaje",
        name_key="tech.reciclaje",
        desc_key="tech.reciclaje_desc",
        branch_key="tech.branch.industry",
        tier=1,
        cost=Cost(COST_TECH_RECICLAJE),
        days=2.0,
        unlock_kinds=(ModuleKind.RECYCLER,),
    ),
    TechDef(
        id="cristalografia",
        name_key="tech.cristalografia",
        desc_key="tech.cristalografia_desc",
        branch_key="tech.branch.extraction",
        tier=2,
        cost=Cost(COST_TECH_CRISTALOGRAFIA),
        days=3.0,
        unlock_kinds=(ModuleKind.CRYSTAL_EXTRACTOR,),
    ),
    TechDef(
        id="almacenamiento",
        name_key="tech.almacenamiento",
        desc_key="tech.almacenamiento_desc",
        branch_key="tech.branch.industry",
        tier=2,
        cost=Cost(COST_TECH_ALMACENAMIENTO),
        days=2.0,
        unlock_kinds=(ModuleKind.BATTERY,),
    ),
)

TECH_BY_ID = {tech.id: tech for tech in TECHS}


def tech_def(tech_id: str) -> TechDef:
    return TECH_BY_ID[tech_id]


def tech_for_module(kind: ModuleKind) -> str | None:
    for tech in TECHS:
        if kind in tech.unlock_kinds:
            return tech.id
    return None
