"""Menú contextual A+A de un módulo, dinámico y sin lógica por módulo en la UI."""

from __future__ import annotations

from dataclasses import dataclass, field

from module_defs import GENERATOR_FUELS, module_active, module_def
from module_kind import ModuleKind
from network import get_connected
from resources import ResourceId, ResourcePool
from world import Module, ModuleState, World


@dataclass(frozen=True)
class ModuleMenuItem:
    action: str
    label_key: str
    enabled: bool = True


@dataclass
class ModuleMenu:
    x: int
    y: int
    kind: ModuleKind
    items: list[ModuleMenuItem] = field(default_factory=list)
    index: int = 0
    page: str = "actions"
    fuel_index: int = 0

    @classmethod
    def open(
        cls,
        world: World,
        mod: Module,
        resources: ResourcePool | None = None,
    ) -> "ModuleMenu":
        connected = (mod.x, mod.y) in get_connected(world)
        active = module_active(mod, connected)
        defn = module_def(mod.kind)
        items: list[ModuleMenuItem] = []

        for action in defn.menu_actions:
            if action == "research":
                items.append(ModuleMenuItem("research", "menu.research", active))
            elif action == "network":
                items.append(ModuleMenuItem("network", "menu.network", active))
            elif action == "fuel":
                items.append(ModuleMenuItem("fuel", "menu.fuel"))

        if defn.can_toggle:
            label = "menu.turn_off" if mod.enabled else "menu.turn_on"
            enabled = mod.state in (ModuleState.ONLINE, ModuleState.OFFLINE)
            if mod.kind == ModuleKind.FUEL_GENERATOR and not mod.enabled:
                enabled = enabled and _generator_can_start(mod, resources)
            items.append(ModuleMenuItem("toggle", label, enabled))

        if mod.kind != ModuleKind.HABITAT:
            items.append(ModuleMenuItem("demolish", "menu.demolish"))

        items.append(ModuleMenuItem("close", "menu.close"))
        return cls(x=mod.x, y=mod.y, kind=mod.kind, items=items)

    def current(self) -> ModuleMenuItem:
        return self.items[self.index % len(self.items)]

    def move(self, delta: int) -> None:
        self.index = (self.index + delta) % len(self.items)

    def open_fuel(self, current: ResourceId | None) -> None:
        self.page = "fuel"
        if current in GENERATOR_FUELS:
            self.fuel_index = GENERATOR_FUELS.index(current)
        else:
            self.fuel_index = 0

    def fuel_move(self, delta: int) -> None:
        self.fuel_index = (self.fuel_index + delta) % len(GENERATOR_FUELS)

    def current_fuel(self) -> ResourceId:
        return GENERATOR_FUELS[self.fuel_index % len(GENERATOR_FUELS)]


def _generator_can_start(mod: Module, resources: ResourcePool | None) -> bool:
    if mod.fuel_resource is None:
        return False
    return resources is None or resources.amount(mod.fuel_resource) > 0.0
