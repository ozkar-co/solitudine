"""Buffers, caps de red y orquestación del tick logístico."""

from __future__ import annotations

from config import (
    HABITAT_COMPONENTS_CAP,
    HABITAT_FOOD_CAP,
    HABITAT_MINERAL_CAP,
    HABITAT_O2_CAP,
    HABITAT_POWER_CAP,
    HABITAT_WATER_CAP,
)
from materials import Stockpile
from module_defs import ModuleKind, module_def
from module_tick import (
    NetworkCaps,
    TickContext,
    apply_power_jobs,
    clamp_pools,
    collect_power_jobs,
    flush_module_buffers,
    tick_solar_production,
)
from network import compute_connected
from resources import ResourcePool
from world import ModuleState, World


class SimulationProxy:
    resources: ResourcePool
    stock: Stockpile


def storage_bonus(world: World, connected: set[tuple[int, int]]) -> float:
    bonus = module_def(ModuleKind.STORAGE).storage_cap_bonus
    return sum(
        bonus
        for mod in world.modules
        if mod.kind == ModuleKind.STORAGE
        and mod.state == ModuleState.ONLINE
        and (mod.x, mod.y) in connected
    )


def network_caps(world: World) -> NetworkCaps:
    connected = compute_connected(world)
    bonus = storage_bonus(world, connected)
    return NetworkCaps(
        o2=HABITAT_O2_CAP + bonus,
        power=HABITAT_POWER_CAP + bonus,
        water=HABITAT_WATER_CAP + bonus,
        food=HABITAT_FOOD_CAP + bonus,
        mineral=HABITAT_MINERAL_CAP + bonus,
        components=HABITAT_COMPONENTS_CAP + bonus,
    )


def apply_modules_dt(
    world: World,
    sim: SimulationProxy,
    dt: float,
    seconds_per_day: float,
    hour_float: float,
) -> None:
    scale = dt / seconds_per_day
    connected = compute_connected(world)
    caps = network_caps(world)
    ctx = TickContext(
        world=world,
        resources=sim.resources,
        stock=sim.stock,
        caps=caps,
        connected=connected,
        scale=scale,
        hour_float=hour_float,
    )
    tick_solar_production(ctx)
    jobs = collect_power_jobs(ctx)
    apply_power_jobs(ctx, jobs)
    flush_module_buffers(ctx)
    clamp_pools(ctx)
