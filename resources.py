"""Recursos, caps, reservas y costes multi-material."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum, StrEnum
from typing import Mapping

from config import (
    ALERT_CRITICAL_DAYS,
    ALERT_WARNING_DAYS,
    HABITAT_COMPONENTS_CAP,
    HABITAT_FOOD_CAP,
    HABITAT_FOOD_DAILY,
    HABITAT_FOOD_START,
    HABITAT_MINERAL_CAP,
    HABITAT_O2_CAP,
    HABITAT_O2_DAILY,
    HABITAT_O2_START,
    HABITAT_POWER_CAP,
    HABITAT_POWER_DAILY,
    HABITAT_POWER_START,
    HABITAT_SCRAP_CAP,
    HABITAT_WATER_CAP,
    HABITAT_WATER_DAILY,
    HABITAT_WATER_START,
    INITIAL_COMPONENTS,
    RESOURCE_RATE_EPSILON,
    RESOURCE_RATE_TAU_DAYS,
    VITAL_EMPTY_THRESHOLD,
)


class ResourceId(StrEnum):
    O2 = "o2"
    POWER = "power"
    WATER = "water"
    FOOD = "food"
    MINERAL = "mineral"
    COMPONENTS = "components"
    SCRAP = "scrap"


@dataclass(frozen=True)
class ResourceDef:
    id: ResourceId
    name_key: str
    short_key: str
    icon: str
    base_cap: float
    lethal: bool = False
    top_bar: bool = False
    alert: bool = False
    storage_bonus: bool = True


RESOURCES: tuple[ResourceDef, ...] = (
    ResourceDef(ResourceId.O2, "resource.o2", "resource.o2.short", "o2", HABITAT_O2_CAP, lethal=True, top_bar=True, alert=True),
    ResourceDef(ResourceId.WATER, "resource.water", "resource.water.short", "water", HABITAT_WATER_CAP, lethal=True, top_bar=True, alert=True),
    ResourceDef(ResourceId.FOOD, "resource.food", "resource.food.short", "food", HABITAT_FOOD_CAP, lethal=True, top_bar=True, alert=True),
    ResourceDef(ResourceId.POWER, "resource.power", "resource.power.short", "power", HABITAT_POWER_CAP, top_bar=True, alert=True),
    ResourceDef(ResourceId.MINERAL, "resource.mineral", "resource.mineral.short", "mineral", HABITAT_MINERAL_CAP),
    ResourceDef(ResourceId.COMPONENTS, "resource.components", "resource.components.short", "components", HABITAT_COMPONENTS_CAP),
    ResourceDef(ResourceId.SCRAP, "resource.scrap", "resource.scrap.short", "scrap", HABITAT_SCRAP_CAP),
)

RESOURCE_BY_ID: dict[ResourceId, ResourceDef] = {defn.id: defn for defn in RESOURCES}
TOPBAR_IDS: tuple[ResourceId, ...] = tuple(defn.id for defn in RESOURCES if defn.top_bar)
ALERT_IDS: tuple[ResourceId, ...] = tuple(defn.id for defn in RESOURCES if defn.alert)
LETHAL_IDS: tuple[ResourceId, ...] = tuple(defn.id for defn in RESOURCES if defn.lethal)


class AlertLevel(IntEnum):
    OK = 0
    WARNING = 1
    CRITICAL = 2


_DEATH_KEYS: dict[ResourceId, str] = {
    ResourceId.O2: "death.o2",
    ResourceId.WATER: "death.water",
    ResourceId.FOOD: "death.food",
}


@dataclass(frozen=True)
class Cost:
    """Coste multi-material. Las claves pueden ser ResourceId o su valor string."""

    amounts: Mapping[ResourceId | str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        normalized: dict[ResourceId, float] = {}
        for key, value in self.amounts.items():
            rid = key if isinstance(key, ResourceId) else ResourceId(key)
            amount = float(value)
            if amount > 0.0:
                normalized[rid] = amount
        object.__setattr__(self, "amounts", normalized)

    @classmethod
    def empty(cls) -> "Cost":
        return cls({})

    def items(self) -> tuple[tuple[ResourceId, float], ...]:
        return tuple(self.amounts.items())

    def can_afford(self, pool: "ResourcePool") -> bool:
        return all(pool.amount(rid) >= amount for rid, amount in self.amounts.items())

    def spend(self, pool: "ResourcePool") -> bool:
        if not self.can_afford(pool):
            return False
        for rid, amount in self.amounts.items():
            pool.set_amount(rid, pool.amount(rid) - amount)
        return True

    def missing(self, pool: "ResourcePool") -> dict[ResourceId, float]:
        return {
            rid: amount - pool.amount(rid)
            for rid, amount in self.amounts.items()
            if pool.amount(rid) < amount
        }

    def refund(self, pool: "ResourcePool", ratio: float, caps: Mapping[ResourceId, float]) -> "Cost":
        if ratio <= 0.0:
            return Cost.empty()
        credited: dict[ResourceId, float] = {}
        for rid, amount in self.amounts.items():
            space = max(0.0, caps.get(rid, float("inf")) - pool.amount(rid))
            credit = min(amount * ratio, space)
            if credit > 0.0:
                pool.add(rid, credit)
                credited[rid] = credit
        return Cost(credited)

    def to_dict(self) -> dict[str, float]:
        return {rid.value: amount for rid, amount in self.amounts.items()}

    @classmethod
    def from_dict(cls, data: Mapping[str, float] | None) -> "Cost":
        return cls(dict(data or {}))

    def __bool__(self) -> bool:
        return bool(self.amounts)


@dataclass
class ResourcePool:
    o2: float = 0.0
    power: float = 0.0
    water: float = 0.0
    food: float = 0.0
    mineral: float = 0.0
    components: float = 0.0
    scrap: float = 0.0
    # Cambio neto por día (solo vitales): positivo = sube, negativo = baja.
    o2_daily: float = 0.0
    power_daily: float = 0.0
    water_daily: float = 0.0
    food_daily: float = 0.0

    @classmethod
    def initial(cls) -> "ResourcePool":
        return cls(
            o2=HABITAT_O2_START,
            power=HABITAT_POWER_START,
            water=HABITAT_WATER_START,
            food=HABITAT_FOOD_START,
            components=INITIAL_COMPONENTS,
            o2_daily=-HABITAT_O2_DAILY,
            power_daily=-HABITAT_POWER_DAILY,
            water_daily=-HABITAT_WATER_DAILY,
            food_daily=-HABITAT_FOOD_DAILY,
        )

    def amount(self, resource: ResourceId) -> float:
        return getattr(self, resource.value)

    def set_amount(self, resource: ResourceId, value: float) -> None:
        setattr(self, resource.value, value)

    def add(self, resource: ResourceId, amount: float) -> None:
        self.set_amount(resource, self.amount(resource) + amount)

    def daily_use(self, resource: ResourceId) -> float:
        """Cambio neto por día (positivo sube, negativo baja)."""
        if resource not in ALERT_IDS:
            return 0.0
        return getattr(self, f"{resource.value}_daily")

    def days_left(self, resource: ResourceId) -> float:
        net = self.daily_use(resource)
        if net >= -RESOURCE_RATE_EPSILON:
            return float("inf")
        return self.amount(resource) / -net

    def update_net_rates(
        self,
        before: tuple[float, float, float, float],
        after: tuple[float, float, float, float],
        dt_days: float,
    ) -> None:
        """Actualiza la tendencia real (EMA) desde los deltas del último tick."""
        if dt_days <= 0.0:
            return
        fields = ("o2_daily", "power_daily", "water_daily", "food_daily")
        alpha = min(1.0, dt_days / RESOURCE_RATE_TAU_DAYS)
        for rate_field, old_amount, new_amount in zip(fields, before, after):
            instant = (new_amount - old_amount) / dt_days
            old_rate = getattr(self, rate_field)
            setattr(self, rate_field, old_rate + (instant - old_rate) * alpha)

    def alert_level(self, resource: ResourceId) -> AlertLevel:
        if resource not in ALERT_IDS:
            return AlertLevel.OK
        days = self.days_left(resource)
        if days == float("inf"):
            return AlertLevel.OK
        if days < ALERT_CRITICAL_DAYS:
            return AlertLevel.CRITICAL
        if days < ALERT_WARNING_DAYS:
            return AlertLevel.WARNING
        return AlertLevel.OK

    def worst_alert(self) -> AlertLevel:
        worst = AlertLevel.OK
        for resource in ALERT_IDS:
            level = self.alert_level(resource)
            if level.value > worst.value:
                worst = level
        return worst

    def apply_vital_flow(self, *, o2: float, water: float, food: float, scale: float) -> None:
        """Consumo vital del hábitat — único punto que muta O₂/agua/comida del astronauta."""
        self.o2 = max(0.0, self.o2 + o2 * scale)
        self.water = max(0.0, self.water + water * scale)
        self.food = max(0.0, self.food + food * scale)

    def clamp(self, caps: Mapping[ResourceId, float]) -> None:
        for defn in RESOURCES:
            self.set_amount(defn.id, min(self.amount(defn.id), caps[defn.id]))

    def _snap_vitals(self) -> None:
        """Alinea reservas residuales con el umbral de muerte (evita 0.04 mostrado como 0.0)."""
        for resource in LETHAL_IDS:
            if self.amount(resource) <= VITAL_EMPTY_THRESHOLD:
                self.set_amount(resource, 0.0)

    def death_cause(self) -> str | None:
        self._snap_vitals()
        for resource in LETHAL_IDS:
            if self.amount(resource) <= 0.0:
                return _DEATH_KEYS[resource]
        return None

    def check_death(self) -> str | None:
        return self.death_cause()
