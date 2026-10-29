"""Definiciones de módulos — única fuente de verdad para flujos, costes y metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from config import (
    BUILD_DAYS_EXTRACTOR,
    BUILD_DAYS_FABRICATOR,
    BUILD_DAYS_CONDENSER,
    BUILD_DAYS_ELECTROLYZER,
    BUILD_DAYS_GREENHOUSE,
    BUILD_DAYS_LABORATORY,
    BUILD_DAYS_LAMP,
    BUILD_DAYS_MINE,
    BUILD_DAYS_RADAR,
    BUILD_DAYS_RECYCLER,
    BUILD_DAYS_SOLAR,
    BUILD_DAYS_STORAGE,
    COST_CABLE,
    COST_EXTRACTOR,
    COST_FABRICATOR,
    COST_CONDENSER,
    COST_ELECTROLYZER,
    COST_GREENHOUSE,
    COST_LABORATORY,
    COST_LAMP,
    COST_MINE,
    COST_RADAR,
    COST_RECYCLER,
    COST_SOLAR,
    COST_STORAGE,
    EXTRACTOR_POWER_DAILY,
    EXTRACTOR_WATER_DAILY,
    ELECTROLYZER_O2_DAILY,
    ELECTROLYZER_POWER_DAILY,
    ELECTROLYZER_WATER_DAILY,
    FABRICATOR_COMPONENTS_DAILY,
    FABRICATOR_MINERAL_DAILY,
    FABRICATOR_POWER_DAILY,
    CONDENSER_POWER_DAILY,
    CONDENSER_WATER_DAILY,
    LABORATORY_POWER_DAILY,
    GREENHOUSE_FOOD_DAILY,
    GREENHOUSE_O2_DAILY,
    GREENHOUSE_POWER_DAILY,
    GREENHOUSE_WATER_DAILY,
    HABITAT_FOOD_DAILY,
    HOURS_PER_DAY,
    HABITAT_O2_DAILY,
    HABITAT_POWER_DAILY,
    HABITAT_LIGHT_RADIUS,
    HABITAT_WATER_DAILY,
    LAMP_LIGHT_RADIUS,
    LAMP_POWER_DAILY,
    MINE_MINERAL_DAILY,
    MINE_POWER_DAILY,
    MODULE_BUFFER_CAP,
    RADAR_POWER_DAILY,
    RECYCLER_COMPONENTS_DAILY,
    RECYCLER_MINERAL_DAILY,
    RECYCLER_POWER_DAILY,
    RECYCLER_SCRAP_DAILY,
    RECYCLER_WATER_DAILY,
    SOLAR_HOUR_END,
    SOLAR_HOUR_START,
    SOLAR_POWER_DAILY,
    STORAGE_NETWORK_BONUS,
)
from module_kind import ModuleKind
from resources import Cost
from world import Deposit, Module, ModuleState, World
from daylight import darkness


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
    scrap: float = 0.0


@dataclass(frozen=True)
class ModuleDef:
    kind: ModuleKind
    nominal: ResourceFlow
    cost: Cost = field(default_factory=Cost.empty)
    build_days: float = 0.0
    has_buffer: bool = False
    buffer_output: BufferOutput | None = None
    placement_deposit: Deposit | None = None
    solar_producer: bool = False
    storage_cap_bonus: float = 0.0
    always_online: bool = False
    can_toggle: bool = True
    light_radius: int = 0
    special_action: str | None = None


MODULE_DEFS: dict[ModuleKind, ModuleDef] = {
    ModuleKind.HABITAT: ModuleDef(
        kind=ModuleKind.HABITAT,
        nominal=ResourceFlow(
            o2=-HABITAT_O2_DAILY,
            power=-HABITAT_POWER_DAILY,
            water=-HABITAT_WATER_DAILY,
            food=-HABITAT_FOOD_DAILY,
        ),
        always_online=True,
        can_toggle=False,
        light_radius=HABITAT_LIGHT_RADIUS,
    ),
    ModuleKind.SOLAR: ModuleDef(
        kind=ModuleKind.SOLAR,
        nominal=ResourceFlow(power=SOLAR_POWER_DAILY),
        cost=Cost(COST_SOLAR),
        build_days=BUILD_DAYS_SOLAR,
        solar_producer=True,
    ),
    ModuleKind.RADAR: ModuleDef(
        kind=ModuleKind.RADAR,
        nominal=ResourceFlow(power=-RADAR_POWER_DAILY),
        cost=Cost(COST_RADAR),
        build_days=BUILD_DAYS_RADAR,
    ),
    ModuleKind.EXTRACTOR: ModuleDef(
        kind=ModuleKind.EXTRACTOR,
        nominal=ResourceFlow(power=-EXTRACTOR_POWER_DAILY, water=EXTRACTOR_WATER_DAILY),
        cost=Cost(COST_EXTRACTOR),
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
        cost=Cost(COST_GREENHOUSE),
        build_days=BUILD_DAYS_GREENHOUSE,
        has_buffer=True,
        buffer_output=BufferOutput.FOOD,
    ),
    ModuleKind.MINE: ModuleDef(
        kind=ModuleKind.MINE,
        nominal=ResourceFlow(power=-MINE_POWER_DAILY, mineral=MINE_MINERAL_DAILY),
        cost=Cost(COST_MINE),
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
        cost=Cost(COST_FABRICATOR),
        build_days=BUILD_DAYS_FABRICATOR,
        has_buffer=True,
        buffer_output=BufferOutput.COMPONENTS,
    ),
    ModuleKind.STORAGE: ModuleDef(
        kind=ModuleKind.STORAGE,
        nominal=ResourceFlow(),
        cost=Cost(COST_STORAGE),
        build_days=BUILD_DAYS_STORAGE,
        storage_cap_bonus=STORAGE_NETWORK_BONUS,
        can_toggle=False,
    ),
    ModuleKind.LAMP: ModuleDef(
        kind=ModuleKind.LAMP,
        nominal=ResourceFlow(power=-LAMP_POWER_DAILY),
        cost=Cost(COST_LAMP),
        build_days=BUILD_DAYS_LAMP,
        light_radius=LAMP_LIGHT_RADIUS,
    ),
    ModuleKind.LABORATORY: ModuleDef(
        kind=ModuleKind.LABORATORY,
        nominal=ResourceFlow(power=-LABORATORY_POWER_DAILY),
        cost=Cost(COST_LABORATORY),
        build_days=BUILD_DAYS_LABORATORY,
        special_action="research",
    ),
    ModuleKind.ELECTROLYZER: ModuleDef(
        kind=ModuleKind.ELECTROLYZER,
        nominal=ResourceFlow(
            power=-ELECTROLYZER_POWER_DAILY,
            water=-ELECTROLYZER_WATER_DAILY,
            o2=ELECTROLYZER_O2_DAILY,
        ),
        cost=Cost(COST_ELECTROLYZER),
        build_days=BUILD_DAYS_ELECTROLYZER,
    ),
    ModuleKind.CONDENSER: ModuleDef(
        kind=ModuleKind.CONDENSER,
        nominal=ResourceFlow(power=-CONDENSER_POWER_DAILY, water=CONDENSER_WATER_DAILY),
        cost=Cost(COST_CONDENSER),
        build_days=BUILD_DAYS_CONDENSER,
    ),
    ModuleKind.RECYCLER: ModuleDef(
        kind=ModuleKind.RECYCLER,
        nominal=ResourceFlow(
            power=-RECYCLER_POWER_DAILY,
            water=-RECYCLER_WATER_DAILY,
            scrap=-RECYCLER_SCRAP_DAILY,
            mineral=RECYCLER_MINERAL_DAILY,
            components=RECYCLER_COMPONENTS_DAILY,
        ),
        cost=Cost(COST_RECYCLER),
        build_days=BUILD_DAYS_RECYCLER,
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
    ModuleKind.LAMP,
    ModuleKind.LABORATORY,
    ModuleKind.ELECTROLYZER,
    ModuleKind.CONDENSER,
    ModuleKind.RECYCLER,
)

CABLE_COST = Cost(COST_CABLE)

_FLOW_KEYS: tuple[tuple[str, str, str], ...] = (
    ("o2", "flow.o2", "flow.o2_use"),
    ("water", "flow.water", "flow.water_use"),
    ("food", "flow.food", "flow.food_use"),
    ("mineral", "flow.mineral", "flow.mineral_use"),
    ("components", "flow.components", "flow.components"),
    ("scrap", "flow.scrap", "flow.scrap_use"),
)


def module_def(kind: ModuleKind) -> ModuleDef:
    return MODULE_DEFS[kind]


def module_active(mod: Module, connected: bool) -> bool:
    """Activo para tick/visión/luz: online, conectado y encendido (salvo hábitat)."""
    defn = MODULE_DEFS[mod.kind]
    if defn.always_online:
        return True
    enabled = mod.enabled if defn.can_toggle else True
    return enabled and mod.state == ModuleState.ONLINE and connected


def buffer_cap(kind: ModuleKind) -> float:
    return MODULE_BUFFER_CAP if MODULE_DEFS[kind].has_buffer else 0.0


@dataclass
class ModuleContext:
    world: World | None = None
    hour_float: float = 12.0
    connected: bool = True


def _is_online(mod: Module, ctx: ModuleContext) -> bool:
    return module_active(mod, ctx.connected)


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
    if mod.kind == ModuleKind.LAMP:
        return ResourceFlow(power=defn.nominal.power * darkness(ctx.hour_float / HOURS_PER_DAY))
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
