"""Buffers por módulo, depósitos finitos y flujo logístico en red."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from config import (
    EXTRACTOR_POWER_DAILY,
    EXTRACTOR_WATER_DAILY,
    FABRICATOR_COMPONENTS_DAILY,
    FABRICATOR_MINERAL_DAILY,
    FABRICATOR_POWER_DAILY,
    GREENHOUSE_FOOD_DAILY,
    GREENHOUSE_O2_DAILY,
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


class SimulationProxy:
    resources: ResourcePool
    stock: Stockpile


@dataclass
class _NetworkCaps:
    o2: float
    power: float
    water: float
    food: float
    mineral: float
    components: float


@dataclass
class _PowerJob:
    power: float
    run: Callable[[float], None]


def _try_add_buffer(mod: Module, amount: float) -> float:
    if mod.buffer_cap <= 0:
        return amount
    space = mod.buffer_cap - mod.buffer
    if space <= 0:
        return 0.0
    added = min(space, amount)
    mod.buffer += added
    return added


def _push(pool: float, cap: float, amount: float) -> tuple[float, float]:
    if amount <= 0:
        return pool, 0.0
    space = cap - pool
    if space <= 0:
        return pool, 0.0
    moved = min(space, amount)
    return pool + moved, moved


def _output_space(mod: Module, pool: float, cap: float) -> float:
    local = max(0.0, mod.buffer_cap - mod.buffer) if mod.buffer_cap > 0 else 0.0
    return local + max(0.0, cap - pool)


def flush_module_buffers(
    world: World,
    sim: SimulationProxy,
    connected: set[tuple[int, int]],
    caps: _NetworkCaps,
) -> None:
    for mod in world.modules:
        if mod.state != ModuleState.ONLINE or (mod.x, mod.y) not in connected:
            continue
        if mod.buffer <= 0:
            continue
        if mod.kind == "extractor":
            sim.resources.water, moved = _push(sim.resources.water, caps.water, mod.buffer)
            mod.buffer -= moved
        elif mod.kind == "greenhouse":
            sim.resources.food, moved = _push(sim.resources.food, caps.food, mod.buffer)
            mod.buffer -= moved
        elif mod.kind == "mine":
            sim.stock.mineral, moved = _push(sim.stock.mineral, caps.mineral, mod.buffer)
            mod.buffer -= moved
        elif mod.kind == "fabricator":
            sim.stock.components, moved = _push(sim.stock.components, caps.components, mod.buffer)
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
    caps = _NetworkCaps(
        o2=HABITAT_O2_CAP + bonus,
        power=HABITAT_POWER_CAP + bonus,
        water=HABITAT_WATER_CAP + bonus,
        food=HABITAT_FOOD_CAP + bonus,
        mineral=HABITAT_MINERAL_CAP + bonus,
        components=HABITAT_COMPONENTS_CAP + bonus,
    )

    solar_active = SOLAR_HOUR_START <= hour_float < SOLAR_HOUR_END
    jobs: list[_PowerJob] = []

    if solar_active:
        for mod in world.modules:
            if (
                mod.kind == "solar"
                and mod.state == ModuleState.ONLINE
                and (mod.x, mod.y) in connected
                and sim.resources.power < caps.power
            ):
                sim.resources.power, _ = _push(
                    sim.resources.power,
                    caps.power,
                    SOLAR_POWER_DAILY * scale,
                )

    for mod in world.modules:
        if mod.state != ModuleState.ONLINE or (mod.x, mod.y) not in connected:
            continue

        if mod.kind == "radar":
            jobs.append(_PowerJob(RADAR_POWER_DAILY * scale, lambda _f: None))
            continue

        if mod.kind == "extractor":
            space = _output_space(mod, sim.resources.water, caps.water)
            if space <= 0:
                continue

            def _run_extractor(f: float, m=mod, sp=space) -> None:
                if f <= 0:
                    return
                want = min(EXTRACTOR_WATER_DAILY * scale * f, sp)
                extracted = world.extract_from_patch(m.x, m.y, Deposit.WATER, want)
                if extracted <= 0:
                    return
                in_buf = _try_add_buffer(m, extracted)
                overflow = extracted - in_buf
                if overflow > 0:
                    sim.resources.water, _ = _push(sim.resources.water, caps.water, overflow)

            jobs.append(_PowerJob(EXTRACTOR_POWER_DAILY * scale, _run_extractor))
            continue

        if mod.kind == "mine":
            space = _output_space(mod, sim.stock.mineral, caps.mineral)
            if space <= 0:
                continue

            def _run_mine(f: float, m=mod, sp=space) -> None:
                if f <= 0:
                    return
                want = min(MINE_MINERAL_DAILY * scale * f, sp)
                extracted = world.extract_from_patch(m.x, m.y, Deposit.MINERAL, want)
                if extracted <= 0:
                    return
                in_buf = _try_add_buffer(m, extracted)
                overflow = extracted - in_buf
                if overflow > 0:
                    sim.stock.mineral, _ = _push(sim.stock.mineral, caps.mineral, overflow)

            jobs.append(_PowerJob(MINE_POWER_DAILY * scale, _run_mine))
            continue

        if mod.kind == "greenhouse":
            food_space = _output_space(mod, sim.resources.food, caps.food)
            o2_space = max(0.0, caps.o2 - sim.resources.o2)
            can_food = food_space > 0 and sim.resources.water > 0
            can_o2 = o2_space > 0
            if not can_food and not can_o2:
                continue
            power = GREENHOUSE_POWER_DAILY * scale if can_food else GREENHOUSE_POWER_DAILY * scale * 0.25

            def _run_greenhouse(f: float, m=mod, fs=food_space, os_=o2_space, cf=can_food) -> None:
                if f <= 0:
                    return
                if os_ > 0:
                    o2_amt = min(GREENHOUSE_O2_DAILY * scale * f, os_)
                    sim.resources.o2, _ = _push(sim.resources.o2, caps.o2, o2_amt)
                if not cf:
                    return
                water_need = GREENHOUSE_WATER_DAILY * scale * f
                if sim.resources.water < water_need:
                    f *= sim.resources.water / water_need if water_need > 0 else 0.0
                    water_need = GREENHOUSE_WATER_DAILY * scale * f
                if f <= 0 or water_need <= 0:
                    return
                sim.resources.water -= water_need
                food_amt = min(GREENHOUSE_FOOD_DAILY * scale * f, fs)
                in_buf = _try_add_buffer(m, food_amt)
                overflow = food_amt - in_buf
                if overflow > 0:
                    sim.resources.food, _ = _push(sim.resources.food, caps.food, overflow)

            jobs.append(_PowerJob(power, _run_greenhouse))
            continue

        if mod.kind == "fabricator":
            space = _output_space(mod, sim.stock.components, caps.components)
            if space <= 0 or sim.stock.mineral <= 0:
                continue

            def _run_fabricator(f: float, m=mod, sp=space) -> None:
                if f <= 0:
                    return
                mineral_need = FABRICATOR_MINERAL_DAILY * scale * f
                mineral_use = min(mineral_need, sim.stock.mineral)
                if mineral_use <= 0:
                    return
                ratio = mineral_use / (FABRICATOR_MINERAL_DAILY * scale) if scale > 0 else 0.0
                sim.stock.mineral -= mineral_use
                cmp_amt = min(FABRICATOR_COMPONENTS_DAILY * scale * ratio, sp)
                in_buf = _try_add_buffer(m, cmp_amt)
                overflow = cmp_amt - in_buf
                if overflow > 0:
                    sim.stock.components, _ = _push(sim.stock.components, caps.components, overflow)

            jobs.append(_PowerJob(FABRICATOR_POWER_DAILY * scale, _run_fabricator))

    total_power = sum(j.power for j in jobs)
    if total_power > 0:
        factor = min(1.0, sim.resources.power / total_power)
        sim.resources.power = max(0.0, sim.resources.power - total_power * factor)
        for job in jobs:
            job.run(factor)

    flush_module_buffers(world, sim, connected, caps)

    sim.resources.o2 = min(sim.resources.o2, caps.o2)
    sim.resources.power = min(sim.resources.power, caps.power)
    sim.resources.water = min(sim.resources.water, caps.water)
    sim.resources.food = min(sim.resources.food, caps.food)
    sim.stock.mineral = min(sim.stock.mineral, caps.mineral)
    sim.stock.components = min(sim.stock.components, caps.components)
