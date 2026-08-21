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


@dataclass
class ResourcePool:
    o2: float
    power: float
    water: float
    food: float
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
            o2_daily=vital.o2,
            power_daily=vital.power,
            water_daily=vital.water,
            food_daily=vital.food,
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

    def consume_astronaut_dt(self, dt: float) -> None:
        """Reservado — consumo vital del hábitat vía module_tick (unificado)."""

    def consume_dt(self, dt: float) -> None:
        pass

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

    def check_death(self) -> str | None:
        if self.o2 <= 0:
            return "death.o2"
        if self.water <= 0:
            return "death.water"
        if self.food <= 0:
            return "death.food"
        return None
