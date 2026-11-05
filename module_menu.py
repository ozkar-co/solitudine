"""Menú contextual A+A de un módulo."""

from __future__ import annotations

from dataclasses import dataclass, field

from module_defs import module_active, module_def
from module_kind import ModuleKind
from network import get_connected
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

    @classmethod
    def open(cls, world: World, mod: Module) -> "ModuleMenu":
        connected = (mod.x, mod.y) in get_connected(world)
        active = module_active(mod, connected)
        defn = module_def(mod.kind)
        items: list[ModuleMenuItem] = []

        if defn.special_action == "research":
            items.append(ModuleMenuItem("research", "menu.research", active))
        elif defn.special_action == "network":
            items.append(ModuleMenuItem("network", "menu.network", active))

        if defn.can_toggle:
            label = "menu.turn_off" if mod.enabled else "menu.turn_on"
            items.append(
                ModuleMenuItem(
                    "toggle",
                    label,
                    mod.state in (ModuleState.ONLINE, ModuleState.OFFLINE),
                )
            )

        if mod.kind != ModuleKind.HABITAT:
            items.append(ModuleMenuItem("demolish", "menu.demolish"))

        items.append(ModuleMenuItem("close", "menu.close"))
        return cls(x=mod.x, y=mod.y, kind=mod.kind, items=items)

    def current(self) -> ModuleMenuItem:
        return self.items[self.index % len(self.items)]

    def move(self, delta: int) -> None:
        self.index = (self.index + delta) % len(self.items)
