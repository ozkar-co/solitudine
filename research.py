"""Estado de investigación — una tecnología a la vez."""

from __future__ import annotations

from dataclasses import dataclass, field

from module_defs import module_active
from module_kind import ModuleKind
from network import get_connected
from resources import ResourcePool
from tech_defs import TECHS, TechDef
from world import World


def active_labs(world: World) -> int:
    connected = get_connected(world)
    return sum(
        1
        for mod in world.modules
        if mod.kind == ModuleKind.LABORATORY and module_active(mod, (mod.x, mod.y) in connected)
    )


def has_active_lab(world: World) -> bool:
    return active_labs(world) > 0


@dataclass
class ResearchState:
    unlocked: set[str] = field(default_factory=set)
    active: str | None = None
    progress: float = 0.0
    selected: int = 0
    open: bool = False

    def selected_tech(self) -> TechDef:
        return TECHS[self.selected % len(TECHS)]

    def select(self, delta: int) -> None:
        self.selected = (self.selected + delta) % len(TECHS)

    def start(self, tech: TechDef, resources: ResourcePool, has_lab: bool) -> bool:
        if self.active is not None or not has_lab:
            return False
        if tech.id in self.unlocked or not set(tech.prereqs).issubset(self.unlocked):
            return False
        if not tech.cost.spend(resources):
            return False
        self.active = tech.id
        self.progress = 0.0
        return True

    def advance(self, days: float) -> None:
        if self.active is None or days <= 0.0:
            return
        tech = TECHS[self._active_index()]
        self.progress += days
        if self.progress >= tech.days:
            self.unlocked.add(tech.id)
            self.active = None
            self.progress = 0.0

    def _active_index(self) -> int:
        for i, tech in enumerate(TECHS):
            if tech.id == self.active:
                return i
        raise KeyError(self.active)
