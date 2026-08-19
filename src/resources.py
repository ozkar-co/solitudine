"""Reservas y consumo del hábitat."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from config import (
    ALERT_CRITICAL_DAYS,
    ALERT_WARNING_DAYS,
    HABITAT_FOOD_DAILY,
    HABITAT_FOOD_START,
    HABITAT_O2_DAILY,
    HABITAT_O2_START,
    HABITAT_POWER_DAILY,
    HABITAT_POWER_START,
    HABITAT_WATER_DAILY,
    HABITAT_WATER_START,
    SECONDS_PER_DAY,
)


class ResourceId(Enum):
    O2 = "o2"
    POWER = "power"
    WATER = "water"
    FOOD = "food"


class AlertLevel(Enum):
    OK = 0
    WARNING = 1
    CRITICAL = 2


@dataclass
class ResourcePool:
    o2: float
    power: float
    water: float
    food: float
    o2_daily: float = HABITAT_O2_DAILY
    power_daily: float = HABITAT_POWER_DAILY
    water_daily: float = HABITAT_WATER_DAILY
    food_daily: float = HABITAT_FOOD_DAILY

    @classmethod
    def initial(cls) -> ResourcePool:
        return cls(
            o2=HABITAT_O2_START,
            power=HABITAT_POWER_START,
            water=HABITAT_WATER_START,
            food=HABITAT_FOOD_START,
        )

    def amount(self, resource: ResourceId) -> float:
        return {
            ResourceId.O2: self.o2,
            ResourceId.POWER: self.power,
            ResourceId.WATER: self.water,
            ResourceId.FOOD: self.food,
        }[resource]

    def daily_use(self, resource: ResourceId) -> float:
        return {
            ResourceId.O2: self.o2_daily,
            ResourceId.POWER: self.power_daily,
            ResourceId.WATER: self.water_daily,
            ResourceId.FOOD: self.food_daily,
        }[resource]

    def days_left(self, resource: ResourceId) -> float:
        daily = self.daily_use(resource)
        if daily <= 0:
            return float("inf")
        return self.amount(resource) / daily

    def alert_level(self, resource: ResourceId) -> AlertLevel:
        days = self.days_left(resource)
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

    def _drain(self, resource: ResourceId, amount: float) -> None:
        if resource == ResourceId.O2:
            self.o2 = max(0.0, self.o2 - amount)
        elif resource == ResourceId.POWER:
            self.power = max(0.0, self.power - amount)
        elif resource == ResourceId.WATER:
            self.water = max(0.0, self.water - amount)
        elif resource == ResourceId.FOOD:
            self.food = max(0.0, self.food - amount)

    def consume_dt(self, dt: float) -> None:
        """Consumo continuo proporcional al tiempo transcurrido."""
        scale = dt / SECONDS_PER_DAY
        self._drain(ResourceId.O2, self.o2_daily * scale)
        self._drain(ResourceId.POWER, self.power_daily * scale)
        self._drain(ResourceId.WATER, self.water_daily * scale)
        self._drain(ResourceId.FOOD, self.food_daily * scale)

    def add_power(self, amount: float) -> None:
        self.power += amount
