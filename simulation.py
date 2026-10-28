"""Reloj de simulación, ticks continuos y construcción."""

from __future__ import annotations

from dataclasses import dataclass, field

from config import HOURS_PER_DAY, SECONDS_PER_DAY
from construction import BuildController
from logistics import apply_modules_dt
from materials import Stockpile
from research import ResearchState, active_labs, has_active_lab
from resources import ResourcePool
from world import World


@dataclass
class Simulation:
    day: int = 1
    day_progress: float = 0.0
    resources: ResourcePool = field(default_factory=ResourcePool.initial)
    stock: Stockpile = field(default_factory=Stockpile)
    build: BuildController = field(default_factory=BuildController)
    research: ResearchState = field(default_factory=ResearchState)
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
        if self.game_over:
            return

        if not self.paused:
            dt_days = dt / SECONDS_PER_DAY
            self.day_progress += dt_days
            while self.day_progress >= 1.0:
                self.day_progress -= 1.0
                self.day += 1
            factor = apply_modules_dt(world, self, dt, SECONDS_PER_DAY, self._hour_float())
            labs = active_labs(world)
            if self.research.active is not None and labs:
                self.research.advance(dt_days * factor * labs)
            self.build.update_sites(world, dt_days)

        self._apply_death_if_needed()

    def start_research(self, world: World) -> bool:
        if self.resources.power <= 0.0:
            return False
        return self.research.start(self.research.selected_tech(), self.stock, has_active_lab(world))

    def _apply_death_if_needed(self) -> None:
        cause = self.resources.death_cause()
        if not cause:
            return
        self.game_over = True
        self.death_cause = cause
        self.paused = True
        self.user_paused = False
        self.build.cancel_build()
