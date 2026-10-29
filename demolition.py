"""Demolición, cancelación de obra y conversión a chatarra."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from config import (
    CANCEL_MAX_RATIO,
    COMPONENT_MINERAL_VALUE,
    DEMOLISH_MAX_RATIO,
    DEMOLISH_MIN_RATIO,
)
from logistics import network_caps
from module_defs import CABLE_COST, ModuleKind, module_def
from network import get_connected
from resources import ResourceId
from vision import on_cable_removed, on_module_removed
from world import Module, ModuleState, World

if TYPE_CHECKING:
    from simulation import Simulation


def can_demolish(world: World, x: int, y: int) -> bool:
    mod = world.module_at(x, y)
    if mod is not None:
        return mod.kind != ModuleKind.HABITAT
    return (x, y) in world.cables


def is_site(mod: Module) -> bool:
    return mod.state in (ModuleState.BUILDING, ModuleState.WAITING)


def _paid_amount(mod: Module, resource: ResourceId) -> float:
    cost = mod.cost_paid if mod.cost_paid else module_def(mod.kind).cost
    return cost.amounts.get(resource, 0.0)


def _mineral_value(mod: Module) -> float:
    return (
        _paid_amount(mod, ResourceId.MINERAL)
        + _paid_amount(mod, ResourceId.COMPONENTS) * COMPONENT_MINERAL_VALUE
    )


def scrap_range(mod: Module) -> tuple[float, float]:
    value = _mineral_value(mod)
    return value * DEMOLISH_MIN_RATIO, value * DEMOLISH_MAX_RATIO


def cancel_scrap(mod: Module) -> float:
    if mod.build_total <= 0.0:
        return 0.0
    progress = min(1.0, max(0.0, mod.build_progress / mod.build_total))
    ratio = min(CANCEL_MAX_RATIO, progress)
    return _paid_amount(mod, ResourceId.COMPONENTS) * ratio


def _add_with_cap(sim: "Simulation", world: World, resource: ResourceId, amount: float) -> float:
    if amount <= 0.0:
        return 0.0
    caps = network_caps(world, get_connected(world))
    space = max(0.0, caps[resource] - sim.resources.amount(resource))
    added = min(amount, space)
    if added > 0.0:
        sim.resources.add(resource, added)
    return added


def _remove_module(world: World, mod: Module) -> None:
    on_module_removed(world, mod)
    if mod in world.modules:
        world.modules.remove(mod)
    world.module_cells.pop((mod.x, mod.y), None)


def _cancel_site(world: World, sim: "Simulation", mod: Module) -> bool:
    scrap = cancel_scrap(mod)
    added = _add_with_cap(sim, world, ResourceId.SCRAP, scrap)
    if added > 0.0:
        sim.stats.scrap_collected += added
    _remove_module(world, mod)
    sim.build.refresh_network(world)
    return True


def _demolish_module(world: World, sim: "Simulation", mod: Module) -> bool:
    scrap = random.uniform(*scrap_range(mod))
    _remove_module(world, mod)
    world.add_ruin(mod.x, mod.y, scrap)
    sim.build.refresh_network(world)
    return True


def _demolish_cable(world: World, sim: "Simulation", x: int, y: int) -> bool:
    world.cables.discard((x, y))
    on_cable_removed(world, x, y)
    refund = CABLE_COST.amounts.get(ResourceId.COMPONENTS, 0.0)
    _add_with_cap(sim, world, ResourceId.COMPONENTS, refund)
    sim.build.refresh_network(world)
    return True


def demolish(world: World, sim: "Simulation", x: int, y: int) -> bool:
    mod = world.module_at(x, y)
    if mod is not None:
        if mod.kind == ModuleKind.HABITAT:
            return False
        if is_site(mod):
            return _cancel_site(world, sim, mod)
        return _demolish_module(world, sim, mod)
    if (x, y) in world.cables:
        return _demolish_cable(world, sim, x, y)
    return False
