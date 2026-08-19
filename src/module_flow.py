"""Producción de agua/comida por módulo (para panel e simulación)."""

from __future__ import annotations

from config import (
    EXTRACTOR_WATER_DAILY,
    GREENHOUSE_FOOD_DAILY,
    GREENHOUSE_WATER_DAILY,
)
from world import Module, ModuleState, World


def module_has_water_source(world: World, mod: Module) -> bool:
    if not world.in_bounds(mod.x, mod.y):
        return False
    i = world.idx(mod.x, mod.y)
    from world import Deposit, Tile

    if Tile(world.tiles[i]) == Tile.WATER:
        return True
    return Deposit(world.deposits[i]) == Deposit.WATER


def module_flow_lines(mod: Module, world: World | None = None) -> list[tuple[str, float]]:
    """Pares (clave i18n, valor/día). Positivo = produce."""
    if mod.state != ModuleState.ONLINE:
        return []
    if mod.kind == "extractor":
        if world is not None and not module_has_water_source(world, mod):
            return []
        return [("flow.water", EXTRACTOR_WATER_DAILY)]
    if mod.kind == "greenhouse":
        return [("flow.food", GREENHOUSE_FOOD_DAILY), ("flow.water_use", -GREENHOUSE_WATER_DAILY)]
    return []
