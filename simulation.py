"""Reloj de simulación, ticks continuos y construcción."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from config import (
    FISH_TRAP_NIGHT_END,
    FISH_TRAP_NIGHT_START,
    FISH_TRAP_ZERO_CHANCE,
    FISH_TRAP_MAX_PER_HOUR,
    HOURS_PER_DAY,
    SECONDS_PER_DAY,
)
from construction import BuildController
from logistics import apply_modules_dt, network_caps
from module_defs import module_active
from module_kind import ModuleKind
from module_menu import ModuleMenu
from network import get_connected
from research import ResearchState, active_labs, has_active_lab
from resources import ResourceId, ResourcePool
from stats import Stats
from world import Tile, World


@dataclass
class Simulation:
    day: int = 1
    day_progress: float = 0.0
    resources: ResourcePool = field(default_factory=ResourcePool.initial)
    stats: Stats = field(default_factory=Stats)
    build: BuildController = field(default_factory=BuildController)
    research: ResearchState = field(default_factory=ResearchState)
    module_menu: ModuleMenu | None = None
    network_open: bool = False
    network_scroll: int = 0
    demolish: tuple[int, int] | None = None
    paused: bool = False
    user_paused: bool = False
    pause_index: int = 0
    credits_open: bool = False
    credits_scroll: int = 0
    credits_konami: str = ""
    easter_egg_open: bool = False
    game_over: bool = False
    death_cause: str = ""
    power_factor: float = 1.0
    rng: random.Random = field(default_factory=random.Random)
    last_hour_index: int = -1

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
            old_hour_index = self.day * HOURS_PER_DAY + int(
                self.day_progress * HOURS_PER_DAY
            )
            self.day_progress += dt_days
            while self.day_progress >= 1.0:
                self.day_progress -= 1.0
                self.day += 1
            new_hour_index = self.day * HOURS_PER_DAY + int(
                self.day_progress * HOURS_PER_DAY
            )
            if self.last_hour_index < 0:
                self.last_hour_index = old_hour_index
            for hour_index in range(self.last_hour_index, new_hour_index):
                hour = hour_index % HOURS_PER_DAY
                if hour >= FISH_TRAP_NIGHT_START or hour < FISH_TRAP_NIGHT_END:
                    self._roll_fish_traps(world)
            self.last_hour_index = new_hour_index
            before = (
                self.resources.o2,
                self.resources.power,
                self.resources.water,
                self.resources.food,
            )
            factor = apply_modules_dt(world, self, dt, SECONDS_PER_DAY, self._hour_float())
            self.power_factor = factor
            after = (
                self.resources.o2,
                self.resources.power,
                self.resources.water,
                self.resources.food,
            )
            self.resources.update_net_rates(before, after, dt_days)
            labs = active_labs(world)
            if self.research.active is not None and labs:
                self.research.advance(dt_days * factor * labs)
            self.build.update_sites(world, dt_days, self.day)

        self._apply_death_if_needed()

    def _roll_fish_traps(self, world: World) -> None:
        connected = get_connected(world)
        caps = network_caps(world, connected)
        for mod in world.modules:
            if mod.kind != ModuleKind.FISH_TRAP:
                continue
            if not module_active(mod, (mod.x, mod.y) in connected):
                continue
            if Tile(world.tiles[world.idx(mod.x, mod.y)]) != Tile.WATER:
                continue
            if self.rng.random() < FISH_TRAP_ZERO_CHANCE:
                continue
            amount = self.rng.uniform(0.0, FISH_TRAP_MAX_PER_HOUR)
            if amount <= 0.0:
                continue
            if mod.buffer_cap > 0:
                space = max(0.0, mod.buffer_cap - mod.buffer)
                added = min(space, amount)
                mod.buffer += added
                amount -= added
            if amount > 0.0:
                space = max(0.0, caps[ResourceId.FOOD] - self.resources.food)
                self.resources.food += min(space, amount)

    def start_research(self, world: World) -> bool:
        if self.resources.power <= 0.0:
            return False
        return self.research.start(self.research.selected_tech(), self.resources, has_active_lab(world))

    def _apply_death_if_needed(self) -> None:
        cause = self.resources.death_cause()
        if not cause:
            return
        self.game_over = True
        self.death_cause = cause
        self.paused = True
        self.user_paused = False
        self.pause_index = 0
        self.credits_open = False
        self.credits_scroll = 0
        self.credits_konami = ""
        self.easter_egg_open = False
        self.demolish = None
        self.build.cancel_build()
