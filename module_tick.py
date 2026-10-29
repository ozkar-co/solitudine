"""Tick de simulación por módulo — consume/produce recursos."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from config import (
    FABRICATOR_COMPONENTS_DAILY,
    FABRICATOR_MINERAL_DAILY,
    GREENHOUSE_FOOD_DAILY,
    GREENHOUSE_O2_DAILY,
    GREENHOUSE_POWER_DAILY,
    GREENHOUSE_WATER_DAILY,
    HOURS_PER_DAY,
    SOLAR_HOUR_END,
    SOLAR_HOUR_START,
)
from daylight import darkness
from module_defs import BufferOutput, ModuleKind, module_active, module_def
from resources import ResourceId, ResourcePool
from stats import Stats
from world import Deposit, Module, World


@dataclass
class TickContext:
    world: World
    resources: ResourcePool
    stats: Stats
    caps: dict[ResourceId, float]
    connected: set[tuple[int, int]]
    scale: float
    hour_float: float


@dataclass
class PowerJob:
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


def _mod_online(mod: Module, ctx: TickContext) -> bool:
    return module_active(mod, (mod.x, mod.y) in ctx.connected)


def tick_solar_production(ctx: TickContext) -> None:
    if not (SOLAR_HOUR_START <= ctx.hour_float < SOLAR_HOUR_END):
        return
    daylight_hours = SOLAR_HOUR_END - SOLAR_HOUR_START
    if daylight_hours <= 0:
        return
    # SOLAR_POWER_DAILY es el total diario; repartir solo en horas de sol.
    solar_scale = ctx.scale * (HOURS_PER_DAY / daylight_hours)
    rate = module_def(ModuleKind.SOLAR).nominal.power
    for mod in ctx.world.modules:
        if mod.kind != ModuleKind.SOLAR or not _mod_online(mod, ctx):
            continue
        if ctx.resources.power >= ctx.caps[ResourceId.POWER]:
            continue
        ctx.resources.power, _ = _push(
            ctx.resources.power,
            ctx.caps[ResourceId.POWER],
            rate * solar_scale,
        )


def tick_habitat_life_support(ctx: TickContext, mod: Module) -> None:
    flow = module_def(ModuleKind.HABITAT).nominal
    ctx.resources.apply_vital_flow(
        o2=flow.o2,
        water=flow.water,
        food=flow.food,
        scale=ctx.scale,
    )


def collect_power_jobs(ctx: TickContext) -> list[PowerJob]:
    jobs: list[PowerJob] = []

    for mod in ctx.world.modules:
        if not _mod_online(mod, ctx):
            continue

        if mod.kind == ModuleKind.HABITAT:
            tick_habitat_life_support(ctx, mod)
            power = abs(module_def(ModuleKind.HABITAT).nominal.power) * ctx.scale
            jobs.append(PowerJob(power, lambda _f: None))
            continue

        if mod.kind == ModuleKind.RADAR:
            jobs.append(PowerJob(abs(module_def(ModuleKind.RADAR).nominal.power) * ctx.scale, lambda _f: None))
            continue

        if mod.kind == ModuleKind.LABORATORY:
            jobs.append(
                PowerJob(abs(module_def(ModuleKind.LABORATORY).nominal.power) * ctx.scale, lambda _f: None)
            )
            continue

        if mod.kind == ModuleKind.LAMP:
            dark = darkness(ctx.hour_float / HOURS_PER_DAY)
            if dark > 0.0:
                power = abs(module_def(ModuleKind.LAMP).nominal.power) * ctx.scale * dark
                jobs.append(PowerJob(power, lambda _f: None))
            continue

        if mod.kind == ModuleKind.EXTRACTOR:
            job = _job_extractor(ctx, mod)
            if job:
                jobs.append(job)
            continue

        if mod.kind == ModuleKind.MINE:
            job = _job_mine(ctx, mod)
            if job:
                jobs.append(job)
            continue

        if mod.kind == ModuleKind.GREENHOUSE:
            job = _job_greenhouse(ctx, mod)
            if job:
                jobs.append(job)
            continue

        if mod.kind == ModuleKind.FABRICATOR:
            job = _job_fabricator(ctx, mod)
            if job:
                jobs.append(job)
            continue

        if mod.kind == ModuleKind.ELECTROLYZER:
            job = _job_electrolyzer(ctx)
            if job:
                jobs.append(job)
            continue

        if mod.kind == ModuleKind.CONDENSER:
            job = _job_condenser(ctx)
            if job:
                jobs.append(job)
            continue

        if mod.kind == ModuleKind.RECYCLER:
            job = _job_recycler(ctx)
            if job:
                jobs.append(job)

    return jobs


def _job_extractor(ctx: TickContext, mod: Module) -> PowerJob | None:
    rate = module_def(ModuleKind.EXTRACTOR).nominal
    if not ctx.world.patch_has_deposit(mod.x, mod.y, Deposit.WATER):
        return None
    space = _output_space(mod, ctx.resources.water, ctx.caps[ResourceId.WATER])
    if space <= 0:
        return None

    def run(f: float, m=mod, sp=space) -> None:
        if f <= 0:
            return
        want = min(rate.water * ctx.scale * f, sp)
        extracted = ctx.world.extract_from_patch(m.x, m.y, Deposit.WATER, want)
        if extracted <= 0:
            return
        in_buf = _try_add_buffer(m, extracted)
        overflow = extracted - in_buf
        if overflow > 0:
            ctx.resources.water, _ = _push(
                ctx.resources.water, ctx.caps[ResourceId.WATER], overflow
            )

    return PowerJob(abs(rate.power) * ctx.scale, run)


def _job_mine(ctx: TickContext, mod: Module) -> PowerJob | None:
    rate = module_def(ModuleKind.MINE).nominal
    if not ctx.world.patch_has_deposit(mod.x, mod.y, Deposit.MINERAL):
        return None
    space = _output_space(mod, ctx.resources.mineral, ctx.caps[ResourceId.MINERAL])
    if space <= 0:
        return None

    def run(f: float, m=mod, sp=space) -> None:
        if f <= 0:
            return
        want = min(rate.mineral * ctx.scale * f, sp)
        extracted = ctx.world.extract_from_patch(m.x, m.y, Deposit.MINERAL, want)
        if extracted <= 0:
            return
        in_buf = _try_add_buffer(m, extracted)
        overflow = extracted - in_buf
        if overflow > 0:
            ctx.resources.mineral, _ = _push(
                ctx.resources.mineral, ctx.caps[ResourceId.MINERAL], overflow
            )

    return PowerJob(abs(rate.power) * ctx.scale, run)


def _job_greenhouse(ctx: TickContext, mod: Module) -> PowerJob | None:
    food_space = _output_space(mod, ctx.resources.food, ctx.caps[ResourceId.FOOD])
    o2_space = max(0.0, ctx.caps[ResourceId.O2] - ctx.resources.o2)
    if ctx.resources.water <= 0.0 or (food_space <= 0 and o2_space <= 0):
        return None
    power = abs(module_def(ModuleKind.GREENHOUSE).nominal.power) * ctx.scale

    def run(f: float, m=mod, fs=food_space, os_=o2_space) -> None:
        if f <= 0:
            return
        water_need = GREENHOUSE_WATER_DAILY * ctx.scale * f
        if ctx.resources.water < water_need:
            f *= ctx.resources.water / water_need if water_need > 0 else 0.0
            water_need = GREENHOUSE_WATER_DAILY * ctx.scale * f
        if f <= 0 or water_need <= 0:
            return
        ctx.resources.water -= water_need
        if os_ > 0:
            o2_amt = min(GREENHOUSE_O2_DAILY * ctx.scale * f, os_)
            ctx.resources.o2, _ = _push(ctx.resources.o2, ctx.caps[ResourceId.O2], o2_amt)
        if fs <= 0:
            return
        food_amt = min(GREENHOUSE_FOOD_DAILY * ctx.scale * f, fs)
        in_buf = _try_add_buffer(m, food_amt)
        overflow = food_amt - in_buf
        if overflow > 0:
            ctx.resources.food, _ = _push(
                ctx.resources.food, ctx.caps[ResourceId.FOOD], overflow
            )

    return PowerJob(power, run)


def _job_fabricator(ctx: TickContext, mod: Module) -> PowerJob | None:
    space = _output_space(
        mod, ctx.resources.components, ctx.caps[ResourceId.COMPONENTS]
    )
    if space <= 0 or ctx.resources.mineral <= 0:
        return None
    rate = module_def(ModuleKind.FABRICATOR).nominal

    def run(f: float, m=mod, sp=space) -> None:
        if f <= 0:
            return
        mineral_need = FABRICATOR_MINERAL_DAILY * ctx.scale * f
        mineral_use = min(mineral_need, ctx.resources.mineral)
        if mineral_use <= 0:
            return
        ratio = mineral_use / (FABRICATOR_MINERAL_DAILY * ctx.scale) if ctx.scale > 0 else 0.0
        ctx.resources.mineral -= mineral_use
        cmp_amt = min(FABRICATOR_COMPONENTS_DAILY * ctx.scale * ratio, sp)
        in_buf = _try_add_buffer(m, cmp_amt)
        overflow = cmp_amt - in_buf
        if overflow > 0:
            ctx.resources.components, _ = _push(
                ctx.resources.components, ctx.caps[ResourceId.COMPONENTS], overflow
            )

    return PowerJob(abs(rate.power) * ctx.scale, run)


def _job_electrolyzer(ctx: TickContext) -> PowerJob | None:
    o2_space = max(0.0, ctx.caps[ResourceId.O2] - ctx.resources.o2)
    if o2_space <= 0.0 or ctx.resources.water <= 0.0:
        return None
    rate = module_def(ModuleKind.ELECTROLYZER).nominal

    def run(f: float, sp=o2_space) -> None:
        if f <= 0.0:
            return
        water_need = abs(rate.water) * ctx.scale * f
        if ctx.resources.water < water_need:
            f *= ctx.resources.water / water_need if water_need > 0 else 0.0
            water_need = abs(rate.water) * ctx.scale * f
        if f <= 0.0 or water_need <= 0.0:
            return
        ctx.resources.water -= water_need
        o2 = min(rate.o2 * ctx.scale * f, sp)
        ctx.resources.o2, _ = _push(ctx.resources.o2, ctx.caps[ResourceId.O2], o2)

    return PowerJob(abs(rate.power) * ctx.scale, run)


def _job_condenser(ctx: TickContext) -> PowerJob | None:
    space = max(0.0, ctx.caps[ResourceId.WATER] - ctx.resources.water)
    if space <= 0.0:
        return None
    rate = module_def(ModuleKind.CONDENSER).nominal

    def run(f: float, sp=space) -> None:
        if f <= 0.0:
            return
        water = min(rate.water * ctx.scale * f, sp)
        ctx.resources.water, _ = _push(
            ctx.resources.water, ctx.caps[ResourceId.WATER], water
        )

    return PowerJob(abs(rate.power) * ctx.scale, run)


def _job_recycler(ctx: TickContext) -> PowerJob | None:
    rate = module_def(ModuleKind.RECYCLER).nominal
    mineral_space = max(0.0, ctx.caps[ResourceId.MINERAL] - ctx.resources.mineral)
    if mineral_space <= 0.0 or ctx.resources.scrap <= 0.0 or ctx.resources.water <= 0.0:
        return None
    power = abs(rate.power) * ctx.scale

    def run(f: float, sp=mineral_space) -> None:
        if f <= 0.0 or ctx.scale <= 0.0:
            return
        scrap_rate = abs(rate.scrap)
        water_rate = abs(rate.water)
        mineral_rate = rate.mineral
        if scrap_rate <= 0.0 or mineral_rate <= 0.0:
            return
        factor = f
        factor = min(factor, ctx.resources.scrap / (scrap_rate * ctx.scale))
        if water_rate > 0.0:
            factor = min(factor, ctx.resources.water / (water_rate * ctx.scale))
        factor = min(factor, sp / (mineral_rate * ctx.scale))
        if factor <= 0.0:
            return
        scrap_use = scrap_rate * ctx.scale * factor
        water_use = water_rate * ctx.scale * factor
        mineral = mineral_rate * ctx.scale * factor
        ctx.resources.scrap = max(0.0, ctx.resources.scrap - scrap_use)
        ctx.resources.water = max(0.0, ctx.resources.water - water_use)
        ctx.resources.mineral = min(
            ctx.caps[ResourceId.MINERAL], ctx.resources.mineral + mineral
        )
        comp_space = max(
            0.0, ctx.caps[ResourceId.COMPONENTS] - ctx.resources.components
        )
        components = min(rate.components * ctx.scale * factor, comp_space)
        ctx.resources.components += components
        ctx.stats.scrap_processed += scrap_use
        ctx.stats.mineral_from_scrap += mineral
        ctx.stats.components_from_scrap += components

    return PowerJob(power, run)


def apply_power_jobs(ctx: TickContext, jobs: list[PowerJob]) -> float:
    total = sum(j.power for j in jobs)
    if total <= 0:
        return 1.0
    factor = min(1.0, ctx.resources.power / total)
    ctx.resources.power = max(0.0, ctx.resources.power - total * factor)
    for job in jobs:
        job.run(factor)
    return factor


def flush_module_buffers(ctx: TickContext) -> None:
    for mod in ctx.world.modules:
        if not _mod_online(mod, ctx) or mod.buffer <= 0:
            continue
        defn = module_def(mod.kind)
        if defn.buffer_output is None:
            continue
        out = defn.buffer_output
        if out == BufferOutput.WATER:
            ctx.resources.water, moved = _push(
                ctx.resources.water, ctx.caps[ResourceId.WATER], mod.buffer
            )
        elif out == BufferOutput.FOOD:
            ctx.resources.food, moved = _push(
                ctx.resources.food, ctx.caps[ResourceId.FOOD], mod.buffer
            )
        elif out == BufferOutput.MINERAL:
            ctx.resources.mineral, moved = _push(
                ctx.resources.mineral, ctx.caps[ResourceId.MINERAL], mod.buffer
            )
        elif out == BufferOutput.COMPONENTS:
            ctx.resources.components, moved = _push(
                ctx.resources.components, ctx.caps[ResourceId.COMPONENTS], mod.buffer
            )
        else:
            continue
        mod.buffer -= moved


def clamp_pools(ctx: TickContext) -> None:
    ctx.resources.clamp(ctx.caps)
