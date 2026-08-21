"""Reloj de simulación, ticks continuos y construcción."""

from __future__ import annotations

from dataclasses import dataclass, field

from config import HOURS_PER_DAY, SECONDS_PER_DAY
from construction import BuildController
from logistics import apply_modules_dt
from materials import Stockpile
from resources import ResourcePool
from world import World


@dataclass
class Simulation:
    day: int = 1
    day_progress: float = 0.0
    resources: ResourcePool = field(default_factory=ResourcePool.initial)
    stock: Stockpile = field(default_factory=Stockpile)
    build: BuildController = field(default_factory=BuildController)
    paused: bool = False
    user_paused: bool = False
    game_over: bool = False
    death_cause: str = ""

    @property
    def hour(self) -> int:
        return min(HOURS_PER_DAY - 1, int(self.day_progress * HOURS_PER_DAY))

    def _hour_float(self) -> float:
        return self.day_progress * HOURS_PER_DAY

    def update(self, dt: float, world: World) -> None:
        if self.paused or self.game_over:
            return
        dt_days = dt / SECONDS_PER_DAY
        self.day_progress += dt_days
        while self.day_progress >= 1.0:
            self.day_progress -= 1.0
            self.day += 1
        apply_modules_dt(world, self, dt, SECONDS_PER_DAY, self._hour_float())
        self.build.update_sites(world, dt_days)
        cause = self.resources.check_death()
        if cause:
            self.game_over = True
            self.death_cause = cause
            self.paused = True
