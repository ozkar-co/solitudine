"""Reloj de simulación y ticks horarios."""

from __future__ import annotations

from dataclasses import dataclass, field

from config import HOURS_PER_DAY, MEALS_PER_DAY, SECONDS_PER_DAY
from resources import ResourcePool


@dataclass
class Simulation:
    day: int = 1
    day_progress: float = 0.0
    resources: ResourcePool = field(default_factory=ResourcePool.initial)
    paused: bool = False
    _tick_hour: int = 0

    @property
    def hour(self) -> int:
        return min(HOURS_PER_DAY - 1, int(self.day_progress * HOURS_PER_DAY))

    def _total_hours(self) -> float:
        return (self.day - 1) * HOURS_PER_DAY + self.day_progress * HOURS_PER_DAY

    def _apply_hour_ticks(self) -> None:
        target = int(self._total_hours())
        while self._tick_hour < target:
            self._tick_hour += 1
            self.resources.consume_hour()
            if self._tick_hour % (HOURS_PER_DAY // MEALS_PER_DAY) == 0:
                self.resources.consume_meal()

    def update(self, dt: float) -> None:
        if self.paused:
            return
        self.day_progress += dt / SECONDS_PER_DAY
        while self.day_progress >= 1.0:
            self.day_progress -= 1.0
            self.day += 1
        self._apply_hour_ticks()
