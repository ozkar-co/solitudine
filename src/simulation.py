"""Reloj de simulación, ticks continuos y construcción."""

from __future__ import annotations

from dataclasses import dataclass, field

from config import (
    HOURS_PER_DAY,
    RADAR_POWER_DAILY,
    SECONDS_PER_DAY,
    SOLAR_HOUR_END,
    SOLAR_HOUR_START,
    SOLAR_POWER_DAILY,
)
from construction import BuildController
from materials import Stockpile
from resources import ResourcePool
from world import ModuleState, World


@dataclass
class Simulation:
    day: int = 1
    day_progress: float = 0.0
    resources: ResourcePool = field(default_factory=ResourcePool.initial)
    stock: Stockpile = field(default_factory=Stockpile)
    build: BuildController = field(default_factory=BuildController)
    paused: bool = False

    @property
    def hour(self) -> int:
        return min(HOURS_PER_DAY - 1, int(self.day_progress * HOURS_PER_DAY))

    def _hour_float(self) -> float:
        return self.day_progress * HOURS_PER_DAY

    def _solar_active(self) -> bool:
        h = self._hour_float()
        return SOLAR_HOUR_START <= h < SOLAR_HOUR_END

    def _apply_modules_dt(self, dt: float, world: World) -> None:
        scale = dt / SECONDS_PER_DAY
        if self._solar_active():
            solar_rate = SOLAR_POWER_DAILY * scale
            for mod in world.modules:
                if mod.kind == "solar" and mod.state == ModuleState.ONLINE:
                    self.resources.add_power(solar_rate)
        radar_rate = RADAR_POWER_DAILY * scale
        for mod in world.modules:
            if mod.kind == "radar" and mod.state == ModuleState.ONLINE:
                self.resources.power = max(0.0, self.resources.power - radar_rate)

    def update(self, dt: float, world: World) -> None:
        if self.paused:
            return
        dt_days = dt / SECONDS_PER_DAY
        self.day_progress += dt_days
        while self.day_progress >= 1.0:
            self.day_progress -= 1.0
            self.day += 1
        self.resources.consume_dt(dt)
        self._apply_modules_dt(dt, world)
        self.build.update_sites(world, dt_days)
        world.reveal_vision()
