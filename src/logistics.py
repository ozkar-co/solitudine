"""Buffers por módulo, depósitos finitos y flujo logístico en red."""

from __future__ import annotations

from config import (
    EXTRACTOR_POWER_DAILY,
    EXTRACTOR_WATER_DAILY,
    FABRICATOR_COMPONENTS_DAILY,
    FABRICATOR_MINERAL_DAILY,
    FABRICATOR_POWER_DAILY,
    GREENHOUSE_FOOD_DAILY,
    GREENHOUSE_POWER_DAILY,
    GREENHOUSE_WATER_DAILY,
    HABITAT_COMPONENTS_CAP,
    HABITAT_FOOD_CAP,
    HABITAT_MINERAL_CAP,
    HABITAT_O2_CAP,
    HABITAT_POWER_CAP,
    HABITAT_WATER_CAP,
    MINE_MINERAL_DAILY,
    MINE_POWER_DAILY,
    MODULE_BUFFER_CAP,
    RADAR_POWER_DAILY,
    SOLAR_HOUR_END,
    SOLAR_HOUR_START,
    SOLAR_POWER_DAILY,
    STORAGE_NETWORK_BONUS,
)
from materials import Stockpile
from network import compute_connected
from resources import ResourcePool
from world import Deposit, Module, ModuleState, Tile, World


def patch_has_deposit(world: World, cx: int, cy: int, kind: Deposit) -> bool:
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            x, y = cx + dx, cy + dy
            if not world.in_bounds(x, y):
                continue
            i = world.idx(x, y)
            if kind == Deposit.WATER:
                if Tile(world.tiles[i]) == Tile.WATER and world.deposit_amounts[i] > 0:
                    return True
                if (
                    Deposit(world.deposits[i]) == Deposit.WATER
                    and world.deposit_amounts[i] > 0
                ):
                    return True
            elif Deposit(world.deposits[i]) == kind and world.deposit_amounts[i] > 0:
                return True
    return False


def storage_bonus(world: World, connected: set[tuple[int, int]]) -> float:
    return sum(
        STORAGE_NETWORK_BONUS
        for mod in world.modules
        if mod.kind == "storage"
        and mod.state == ModuleState.ONLINE
        and (mod.x, mod.y) in connected
    )


def _try_add_buffer(mod: Module, amount: float) -> float:
    """Añade a buffer local; devuelve lo que cupo."""
    if mod.buffer_cap <= 0:
        return amount
    space = mod.buffer_cap - mod.buffer
    if space <= 0:
        return 0.0
    added = min(space, amount)
    mod.buffer += added
    return added


def _push_water(sim: SimulationProxy, amount: float, cap: float) -> float:
    space = cap - sim.resources.water
    if space <= 0:
        return 0.0
    moved = min(space, amount)
    sim.resources.water += moved
    return moved


def _push_food(sim: SimulationProxy, amount: float, cap: float) -> float:
    space = cap - sim.resources.food
    if space <= 0:
        return 0.0
    moved = min(space, amount)
    sim.resources.food += moved
    return moved


def _push_power(sim: SimulationProxy, amount: float, cap: float) -> float:
    space = cap - sim.resources.power
    if space <= 0:
        return 0.0
    moved = min(space, amount)
    sim.resources.power += moved
    return moved


def _push_mineral(stock: Stockpile, amount: float, cap: float) -> float:
    space = cap - stock.mineral
    if space <= 0:
        return 0.0
    moved = min(space, amount)
    stock.mineral += moved
    return moved


def _push_components(stock: Stockpile, amount: float, cap: float) -> float:
    space = cap - stock.components
    if space <= 0:
        return 0.0
    moved = min(space, amount)
    stock.components += moved
    return moved


class SimulationProxy:
    """Evita import circular; simulation pasa self."""

    resources: ResourcePool
    stock: Stockpile


def flush_module_buffers(
    world: World,
    sim: SimulationProxy,
    connected: set[tuple[int, int]],
) -> None:
    bonus = storage_bonus(world, connected)
    water_cap = HABITAT_WATER_CAP + bonus
    food_cap = HABITAT_FOOD_CAP + bonus
    power_cap = HABITAT_POWER_CAP + bonus
    mineral_cap = HABITAT_MINERAL_CAP + bonus
    components_cap = HABITAT_COMPONENTS_CAP + bonus

    for mod in world.modules:
        if mod.state != ModuleState.ONLINE or (mod.x, mod.y) not in connected:
            continue
        if mod.buffer <= 0:
            continue
        if mod.kind == "extractor":
            moved = _push_water(sim, mod.buffer, water_cap)
            mod.buffer -= moved
        elif mod.kind == "greenhouse":
            moved = _push_food(sim, mod.buffer, food_cap)
            mod.buffer -= moved
        elif mod.kind == "solar":
            moved = _push_power(sim, mod.buffer, power_cap)
            mod.buffer -= moved
        elif mod.kind == "mine":
            moved = _push_mineral(sim.stock, mod.buffer, mineral_cap)
            mod.buffer -= moved
        elif mod.kind == "fabricator":
            moved = _push_components(sim.stock, mod.buffer, components_cap)
            mod.buffer -= moved


def apply_modules_dt(
    world: World,
    sim: SimulationProxy,
    dt: float,
    seconds_per_day: float,
    hour_float: float,
) -> None:
    scale = dt / seconds_per_day
    connected = compute_connected(world)
    bonus = storage_bonus(world, connected)
    water_cap = HABITAT_WATER_CAP + bonus
    food_cap = HABITAT_FOOD_CAP + bonus
    power_cap = HABITAT_POWER_CAP + bonus
    mineral_cap = HABITAT_MINERAL_CAP + bonus
    components_cap = HABITAT_COMPONENTS_CAP + bonus

    solar_active = SOLAR_HOUR_START <= hour_float < SOLAR_HOUR_END

    for mod in world.modules:
        if mod.state != ModuleState.ONLINE or (mod.x, mod.y) not in connected:
            continue

        if mod.kind == "radar":
            sim.resources.power = max(0.0, sim.resources.power - RADAR_POWER_DAILY * scale)

        elif mod.kind == "solar" and solar_active:
            if mod.buffer >= mod.buffer_cap and sim.resources.power >= power_cap:
                continue
            want = SOLAR_POWER_DAILY * scale
            produced = _try_add_buffer(mod, want)
            if produced < want:
                _push_power(sim, want - produced, power_cap)

        elif mod.kind == "extractor":
            if mod.buffer >= mod.buffer_cap and sim.resources.water >= water_cap:
                continue
            want = EXTRACTOR_WATER_DAILY * scale
            extracted = world.extract_from_patch(mod.x, mod.y, Deposit.WATER, want)
            if extracted <= 0:
                continue
            sim.resources.power = max(0.0, sim.resources.power - EXTRACTOR_POWER_DAILY * scale)
            produced = _try_add_buffer(mod, extracted)
            if produced < extracted:
                _push_water(sim, extracted - produced, water_cap)

        elif mod.kind == "mine":
            if mod.buffer >= mod.buffer_cap and sim.stock.mineral >= mineral_cap:
                continue
            want = MINE_MINERAL_DAILY * scale
            extracted = world.extract_from_patch(mod.x, mod.y, Deposit.MINERAL, want)
            if extracted <= 0:
                continue
            sim.resources.power = max(0.0, sim.resources.power - MINE_POWER_DAILY * scale)
            produced = _try_add_buffer(mod, extracted)
            if produced < extracted:
                _push_mineral(sim.stock, extracted - produced, mineral_cap)

        elif mod.kind == "greenhouse":
            if mod.buffer >= mod.buffer_cap and sim.resources.food >= food_cap:
                continue
            want = GREENHOUSE_FOOD_DAILY * scale
            water_need = GREENHOUSE_WATER_DAILY * scale
            if sim.resources.water < water_need:
                continue
            sim.resources.water -= water_need
            sim.resources.power = max(0.0, sim.resources.power - GREENHOUSE_POWER_DAILY * scale)
            produced = _try_add_buffer(mod, want)
            if produced < want:
                _push_food(sim, want - produced, food_cap)

        elif mod.kind == "fabricator":
            if mod.buffer >= mod.buffer_cap and sim.stock.components >= components_cap:
                continue
            want = FABRICATOR_COMPONENTS_DAILY * scale
            mineral_need = FABRICATOR_MINERAL_DAILY * scale
            if sim.stock.mineral < mineral_need:
                continue
            sim.stock.mineral -= mineral_need
            sim.resources.power = max(0.0, sim.resources.power - FABRICATOR_POWER_DAILY * scale)
            produced = _try_add_buffer(mod, want)
            if produced < want:
                _push_components(sim.stock, want - produced, components_cap)

    flush_module_buffers(world, sim, connected)

    # Clamp pools to caps
    sim.resources.o2 = min(sim.resources.o2, HABITAT_O2_CAP + bonus)
    sim.resources.power = min(sim.resources.power, power_cap)
    sim.resources.water = min(sim.resources.water, water_cap)
    sim.resources.food = min(sim.resources.food, food_cap)
    sim.stock.mineral = min(sim.stock.mineral, mineral_cap)
    sim.stock.components = min(sim.stock.components, components_cap)
