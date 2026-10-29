"""Reservas y consumo del hábitat."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from config import (
    ALERT_CRITICAL_DAYS,
    ALERT_WARNING_DAYS,
    HABITAT_FOOD_START,
    HABITAT_O2_START,
    HABITAT_POWER_START,
    HABITAT_WATER_START,
    RESOURCE_RATE_EPSILON,
    RESOURCE_RATE_TAU_DAYS,
    VITAL_EMPTY_THRESHOLD,
)
from module_defs import habitat_daily_consumption


class ResourceId(Enum):
    O2 = "o2"
    POWER = "power"
    WATER = "water"
    FOOD = "food"


class AlertLevel(Enum):
    OK = 0
    WARNING = 1
    CRITICAL = 2


_VITAL_DEATH_ORDER: tuple[tuple[ResourceId, str], ...] = (
    (ResourceId.O2, "death.o2"),
    (ResourceId.WATER, "death.water"),
    (ResourceId.FOOD, "death.food"),
)


@dataclass
class ResourcePool:
    o2: float
    power: float
    water: float
    food: float
    # Cambio neto por día: positivo = sube, negativo = baja.
    o2_daily: float = 0.0
    power_daily: float = 0.0
    water_daily: float = 0.0
    food_daily: float = 0.0

    @classmethod
    def initial(cls) -> ResourcePool:
        vital = habitat_daily_consumption()
        return cls(
            o2=HABITAT_O2_START,
            power=HABITAT_POWER_START,
            water=HABITAT_WATER_START,
            food=HABITAT_FOOD_START,
            o2_daily=-vital.o2,
            power_daily=-vital.power,
            water_daily=-vital.water,
            food_daily=-vital.food,
        )

    def amount(self, resource: ResourceId) -> float:
        return {
            ResourceId.O2: self.o2,
            ResourceId.POWER: self.power,
            ResourceId.WATER: self.water,
            ResourceId.FOOD: self.food,
        }[resource]

    def daily_use(self, resource: ResourceId) -> float:
        """Cambio neto por día (positivo sube, negativo baja)."""
        return {
            ResourceId.O2: self.o2_daily,
            ResourceId.POWER: self.power_daily,
            ResourceId.WATER: self.water_daily,
            ResourceId.FOOD: self.food_daily,
        }[resource]

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
        for resource in ResourceId:
            level = self.alert_level(resource)
            if level.value > worst.value:
                worst = level
        return worst

    def apply_vital_flow(self, *, o2: float, water: float, food: float, scale: float) -> None:
        """Consumo vital del hábitat — único punto que muta O₂/agua/comida del astronauta."""
        self.o2 = max(0.0, self.o2 + o2 * scale)
        self.water = max(0.0, self.water + water * scale)
        self.food = max(0.0, self.food + food * scale)

    def add_power(self, amount: float) -> None:
        self.power += amount

    def add_water(self, amount: float) -> None:
        self.water += amount

    def add_food(self, amount: float) -> None:
        self.food += amount

    def clamp_to(self, o2_cap: float, power_cap: float, water_cap: float, food_cap: float) -> None:
        self.o2 = min(self.o2, o2_cap)
        self.power = min(self.power, power_cap)
        self.water = min(self.water, water_cap)
        self.food = min(self.food, food_cap)

    def _snap_vitals(self) -> None:
        """Alinea reservas residuales con el umbral de muerte (evita 0.04 mostrado como 0.0)."""
        for resource in (ResourceId.O2, ResourceId.WATER, ResourceId.FOOD):
            amount = self.amount(resource)
            if amount <= VITAL_EMPTY_THRESHOLD:
                if resource == ResourceId.O2:
                    self.o2 = 0.0
                elif resource == ResourceId.WATER:
                    self.water = 0.0
                else:
                    self.food = 0.0

    def death_cause(self) -> str | None:
        self._snap_vitals()
        for resource, key in _VITAL_DEATH_ORDER:
            if self.amount(resource) <= 0.0:
                return key
        return None

    def check_death(self) -> str | None:
        return self.death_cause()
