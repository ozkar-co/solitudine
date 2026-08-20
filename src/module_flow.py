"""Producción por módulo (panel y simulación)."""

from __future__ import annotations

from config import (
    EXTRACTOR_WATER_DAILY,
    FABRICATOR_COMPONENTS_DAILY,
    FABRICATOR_MINERAL_DAILY,
    GREENHOUSE_FOOD_DAILY,
    GREENHOUSE_O2_DAILY,
    GREENHOUSE_WATER_DAILY,
    HABITAT_FOOD_DAILY,
    HABITAT_O2_DAILY,
    HABITAT_WATER_DAILY,
    MINE_MINERAL_DAILY,
)
from logistics import patch_has_deposit
from world import Deposit, Module, ModuleState, World


def module_flow_lines(mod: Module, world: World | None = None) -> list[tuple[str, float]]:
    if mod.kind == "habitat":
        return [
            ("flow.o2_use", -HABITAT_O2_DAILY),
            ("flow.water_use", -HABITAT_WATER_DAILY),
            ("flow.food_use", -HABITAT_FOOD_DAILY),
        ]
    if mod.state != ModuleState.ONLINE:
        return []
    if mod.kind == "extractor":
        if world is not None and not patch_has_deposit(world, mod.x, mod.y, Deposit.WATER):
            return []
        return [("flow.water", EXTRACTOR_WATER_DAILY)]
    if mod.kind == "mine":
        if world is not None and not patch_has_deposit(world, mod.x, mod.y, Deposit.MINERAL):
            return []
        return [("flow.mineral", MINE_MINERAL_DAILY)]
    if mod.kind == "fabricator":
        return [
            ("flow.components", FABRICATOR_COMPONENTS_DAILY),
            ("flow.mineral_use", -FABRICATOR_MINERAL_DAILY),
        ]
    if mod.kind == "greenhouse":
        return [
            ("flow.food", GREENHOUSE_FOOD_DAILY),
            ("flow.water_use", -GREENHOUSE_WATER_DAILY),
            ("flow.o2", GREENHOUSE_O2_DAILY),
        ]
    return []
