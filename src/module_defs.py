"""Definiciones de módulos — única fuente de verdad para flujos, costes y metadata."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from config import (
    BUILD_DAYS_EXTRACTOR,
    BUILD_DAYS_FABRICATOR,
    BUILD_DAYS_GREENHOUSE,
    BUILD_DAYS_MINE,
    BUILD_DAYS_RADAR,
    BUILD_DAYS_SOLAR,
    BUILD_DAYS_STORAGE,
    COST_CABLE,
    COST_EXTRACTOR,
    COST_FABRICATOR,
    COST_GREENHOUSE,
    COST_MINE,
    COST_RADAR,
    COST_SOLAR,
    COST_STORAGE,
    EXTRACTOR_POWER_DAILY,
    EXTRACTOR_WATER_DAILY,
    FABRICATOR_COMPONENTS_DAILY,
    FABRICATOR_MINERAL_DAILY,
    FABRICATOR_POWER_DAILY,
    GREENHOUSE_FOOD_DAILY,
    GREENHOUSE_O2_DAILY,
    GREENHOUSE_POWER_DAILY,
    GREENHOUSE_WATER_DAILY,
    HABITAT_FOOD_DAILY,
    HABITAT_O2_DAILY,
    HABITAT_POWER_DAILY,
    HABITAT_WATER_DAILY,
    MINE_MINERAL_DAILY,
    MINE_POWER_DAILY,
    MODULE_BUFFER_CAP,
    RADAR_POWER_DAILY,
    SOLAR_HOUR_END,
    SOLAR_HOUR_START,
    SOLAR_POWER_DAILY,
    STORAGE_NETWORK_BONUS,
)
from module_kind import ModuleKind
from world import Deposit, Module, ModuleState, World


class BufferOutput(StrEnum):
    WATER = "water"
    FOOD = "food"
    MINERAL = "mineral"
    COMPONENTS = "components"


@dataclass(frozen=True)
class ResourceFlow:
    """Unidades/día: positivo = produce, negativo = consume."""

    o2: float = 0.0
    power: float = 0.0
    water: float = 0.0
    food: float = 0.0
    mineral: float = 0.0
    components: float = 0.0


@dataclass(frozen=True)
class ModuleDef:
    kind: ModuleKind
    nominal: ResourceFlow
    color: tuple[int, int, int]
    cost: float = 0.0
    build_days: float = 0.0
    has_buffer: bool = False
    buffer_output: BufferOutput | None = None
    placement_deposit: Deposit | None = None
    solar_producer: bool = False
    storage_cap_bonus: float = 0.0
    always_online: bool = False


# --- Colores (referenciados por ui_theme) ---
COL_HABITAT = (220, 200, 80)
COL_SOLAR = (255, 140, 40)
COL_RADAR = (80, 220, 220)
COL_EXTRACTOR = (60, 150, 230)
COL_GREENHOUSE = (90, 200, 70)
COL_MINE = (140, 110, 75)
COL_FABRICATOR = (200, 120, 180)
COL_STORAGE = (170, 170, 90)

MODULE_DEFS: dict[ModuleKind, ModuleDef] = {
    ModuleKind.HABITAT: ModuleDef(
        kind=ModuleKind.HABITAT,
        nominal=ResourceFlow(
            o2=-HABITAT_O2_DAILY,
            power=-HABITAT_POWER_DAILY,
            water=-HABITAT_WATER_DAILY,
            food=-HABITAT_FOOD_DAILY,
        ),
        color=COL_HABITAT,
        always_online=True,
    ),
    ModuleKind.SOLAR: ModuleDef(
        kind=ModuleKind.SOLAR,
        nominal=ResourceFlow(power=SOLAR_POWER_DAILY),
        color=COL_SOLAR,
        cost=COST_SOLAR,
        build_days=BUILD_DAYS_SOLAR,
        solar_producer=True,
    ),
    ModuleKind.RADAR: ModuleDef(
        kind=ModuleKind.RADAR,
        nominal=ResourceFlow(power=-RADAR_POWER_DAILY),
        color=COL_RADAR,
        cost=COST_RADAR,
        build_days=BUILD_DAYS_RADAR,
    ),
    ModuleKind.EXTRACTOR: ModuleDef(
        kind=ModuleKind.EXTRACTOR,
        nominal=ResourceFlow(power=-EXTRACTOR_POWER_DAILY, water=EXTRACTOR_WATER_DAILY),
        color=COL_EXTRACTOR,
        cost=COST_EXTRACTOR,
        build_days=BUILD_DAYS_EXTRACTOR,
        has_buffer=True,
        buffer_output=BufferOutput.WATER,
        placement_deposit=Deposit.WATER,
    ),
    ModuleKind.GREENHOUSE: ModuleDef(
        kind=ModuleKind.GREENHOUSE,
        nominal=ResourceFlow(
            power=-GREENHOUSE_POWER_DAILY,
            water=-GREENHOUSE_WATER_DAILY,
            food=GREENHOUSE_FOOD_DAILY,
            o2=GREENHOUSE_O2_DAILY,
        ),
        color=COL_GREENHOUSE,
        cost=COST_GREENHOUSE,
        build_days=BUILD_DAYS_GREENHOUSE,
        has_buffer=True,
        buffer_output=BufferOutput.FOOD,
    ),
    ModuleKind.MINE: ModuleDef(
        kind=ModuleKind.MINE,
        nominal=ResourceFlow(power=-MINE_POWER_DAILY, mineral=MINE_MINERAL_DAILY),
        color=COL_MINE,
        cost=COST_MINE,
        build_days=BUILD_DAYS_MINE,
        has_buffer=True,
        buffer_output=BufferOutput.MINERAL,
        placement_deposit=Deposit.MINERAL,
    ),
    ModuleKind.FABRICATOR: ModuleDef(
        kind=ModuleKind.FABRICATOR,
        nominal=ResourceFlow(
            power=-FABRICATOR_POWER_DAILY,
            mineral=-FABRICATOR_MINERAL_DAILY,
            components=FABRICATOR_COMPONENTS_DAILY,
        ),
        color=COL_FABRICATOR,
        cost=COST_FABRICATOR,
        build_days=BUILD_DAYS_FABRICATOR,
        has_buffer=True,
        buffer_output=BufferOutput.COMPONENTS,
    ),
    ModuleKind.STORAGE: ModuleDef(
        kind=ModuleKind.STORAGE,
        nominal=ResourceFlow(),
        color=COL_STORAGE,
        cost=COST_STORAGE,
        build_days=BUILD_DAYS_STORAGE,
        storage_cap_bonus=STORAGE_NETWORK_BONUS,
    ),
}

BUILDABLE_KINDS: tuple[ModuleKind, ...] = (
    ModuleKind.SOLAR,
    ModuleKind.EXTRACTOR,
    ModuleKind.MINE,
    ModuleKind.FABRICATOR,
    ModuleKind.GREENHOUSE,
    ModuleKind.STORAGE,
    ModuleKind.RADAR,
)

CABLE_COST = COST_CABLE

_FLOW_KEYS: tuple[tuple[str, str, str], ...] = (
    ("o2", "flow.o2", "flow.o2_use"),
    ("water", "flow.water", "flow.water_use"),
    ("food", "flow.food", "flow.food_use"),
    ("mineral", "flow.mineral", "flow.mineral_use"),
    ("components", "flow.components", "flow.components"),
)


def module_def(kind: ModuleKind) -> ModuleDef:
    return MODULE_DEFS[kind]


def buffer_cap(kind: ModuleKind) -> float:
    return MODULE_BUFFER_CAP if MODULE_DEFS[kind].has_buffer else 0.0


def module_colors() -> dict[str, tuple[int, int, int]]:
    return {k.value: d.color for k, d in MODULE_DEFS.items()}


@dataclass
class ModuleContext:
    world: World | None = None
    hour_float: float = 12.0
    connected: bool = True


def _is_online(mod: Module, ctx: ModuleContext) -> bool:
    defn = module_def(mod.kind)
    if defn.always_online:
        return True
    return mod.state == ModuleState.ONLINE and ctx.connected


def _solar_active(hour_float: float) -> bool:
    return SOLAR_HOUR_START <= hour_float < SOLAR_HOUR_END


def _has_deposit(mod: Module, ctx: ModuleContext) -> bool:
    if ctx.world is None:
        return True
    defn = module_def(mod.kind)
    if defn.placement_deposit is None:
        return True
    return ctx.world.patch_has_deposit(mod.x, mod.y, defn.placement_deposit)


def effective_flow(mod: Module, ctx: ModuleContext) -> ResourceFlow:
    """Flujos nominales cuando el módulo estaría activo (para panel)."""
    if not _is_online(mod, ctx):
        return ResourceFlow()
    defn = module_def(mod.kind)
    flow = defn.nominal
    if defn.solar_producer and not _solar_active(ctx.hour_float):
        return ResourceFlow()
    if defn.placement_deposit is not None and not _has_deposit(mod, ctx):
        return ResourceFlow()
    return flow


def panel_flow_lines(mod: Module, ctx: ModuleContext) -> list[tuple[str, float]]:
    flow = effective_flow(mod, ctx)
    lines: list[tuple[str, float]] = []
    for field, pos_key, neg_key in _FLOW_KEYS:
        value = getattr(flow, field)
        if value == 0.0:
            continue
        key = pos_key if value > 0 else neg_key
        lines.append((key, value))
    return lines


def panel_power_daily(mod: Module, ctx: ModuleContext) -> float:
    return effective_flow(mod, ctx).power


def habitat_daily_consumption() -> ResourceFlow:
    """Consumo vital del hábitat (valores positivos = cantidad consumida/día)."""
    flow = module_def(ModuleKind.HABITAT).nominal
    return ResourceFlow(
        o2=abs(flow.o2),
        power=abs(flow.power),
        water=abs(flow.water),
        food=abs(flow.food),
    )
