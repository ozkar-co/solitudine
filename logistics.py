"""Buffers, caps de red y orquestación del tick logístico."""

from __future__ import annotations

from module_defs import ModuleKind, module_active, module_def
from module_tick import (
    TickContext,
    apply_power_jobs,
    clamp_pools,
    collect_power_jobs,
    flush_module_buffers,
    tick_fuel_production,
    tick_solar_production,
)
from network import get_connected
from resources import RESOURCES, ResourceId, ResourcePool
from stats import Stats
from world import World


class SimulationProxy:
    resources: ResourcePool
    stats: Stats


def storage_bonuses(
    world: World,
    connected: set[tuple[int, int]],
) -> dict[ResourceId, float]:
    """Bonos de cap por recurso: general y almacenamientos especializados."""
    bonuses = {defn.id: 0.0 for defn in RESOURCES}
    for mod in world.modules:
        if not module_active(mod, (mod.x, mod.y) in connected):
            continue
        defn = module_def(mod.kind)
        if defn.storage_cap_bonus > 0.0:
            for resource in RESOURCES:
                if resource.storage_bonus:
                    bonuses[resource.id] += defn.storage_cap_bonus
        for resource, amount in defn.storage_caps.items():
            bonuses[resource] += amount
    return bonuses


def network_caps(
    world: World,
    connected: set[tuple[int, int]] | None = None,
) -> dict[ResourceId, float]:
    if connected is None:
        connected = get_connected(world)
    bonuses = storage_bonuses(world, connected)
    return {
        defn.id: defn.base_cap + bonuses[defn.id]
        for defn in RESOURCES
    }


def apply_modules_dt(
    world: World,
    sim: SimulationProxy,
    dt: float,
    seconds_per_day: float,
    hour_float: float,
) -> float:
    scale = dt / seconds_per_day
    connected = get_connected(world)
    caps = network_caps(world, connected)
    ctx = TickContext(
        world=world,
        resources=sim.resources,
        stats=sim.stats,
        caps=caps,
        connected=connected,
        scale=scale,
        hour_float=hour_float,
    )
    tick_fuel_production(ctx)
    tick_solar_production(ctx)
    jobs = collect_power_jobs(ctx)
    factor = apply_power_jobs(ctx, jobs)
    flush_module_buffers(ctx)
    clamp_pools(ctx)
    return factor
