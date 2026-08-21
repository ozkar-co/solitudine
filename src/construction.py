"""Modos y acciones de construcción."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from materials import Stockpile
from module_defs import CABLE_COST, ModuleKind, module_def
from network import get_connected, invalidate_network_cache, is_adjacent_to_network
from vision import on_cable_added, on_module_built, on_module_online_changed
from world import Deposit, Module, ModuleState, Tile, World


class BuildKind(Enum):
    CABLE = auto()
    SOLAR = auto()
    EXTRACTOR = auto()
    MINE = auto()
    FABRICATOR = auto()
    GREENHOUSE = auto()
    STORAGE = auto()
    RADAR = auto()


BUILD_KINDS = (
    BuildKind.CABLE,
    BuildKind.SOLAR,
    BuildKind.EXTRACTOR,
    BuildKind.MINE,
    BuildKind.FABRICATOR,
    BuildKind.GREENHOUSE,
    BuildKind.STORAGE,
    BuildKind.RADAR,
)


class BuildMode(Enum):
    NONE = auto()
    MENU = auto()
    PLACE = auto()


BUILD_TO_MODULE: dict[BuildKind, ModuleKind] = {
    BuildKind.SOLAR: ModuleKind.SOLAR,
    BuildKind.RADAR: ModuleKind.RADAR,
    BuildKind.EXTRACTOR: ModuleKind.EXTRACTOR,
    BuildKind.GREENHOUSE: ModuleKind.GREENHOUSE,
    BuildKind.MINE: ModuleKind.MINE,
    BuildKind.FABRICATOR: ModuleKind.FABRICATOR,
    BuildKind.STORAGE: ModuleKind.STORAGE,
}


def kind_cost(kind: BuildKind) -> float:
    if kind == BuildKind.CABLE:
        return CABLE_COST
    return module_def(BUILD_TO_MODULE[kind]).cost


def kind_build_days(kind: BuildKind) -> float:
    if kind == BuildKind.CABLE:
        return 0.0
    return module_def(BUILD_TO_MODULE[kind]).build_days


def module_kind_for(build: BuildKind) -> ModuleKind:
    return BUILD_TO_MODULE[build]


@dataclass
class BuildController:
    mode: BuildMode = BuildMode.NONE
    selected: BuildKind = BuildKind.CABLE
    menu_index: int = 0
    cable_chain: list[tuple[int, int]] = field(default_factory=list)

    def enter_menu(self) -> None:
        self.mode = BuildMode.MENU
        self.menu_index = 0
        self.selected = BUILD_KINDS[self.menu_index]
        self.cable_chain.clear()

    def exit_menu(self) -> None:
        self.mode = BuildMode.NONE
        self.cable_chain.clear()

    def menu_up(self) -> None:
        if self.mode != BuildMode.MENU:
            return
        self.menu_index = (self.menu_index - 1) % len(BUILD_KINDS)
        self.selected = BUILD_KINDS[self.menu_index]

    def menu_down(self) -> None:
        if self.mode != BuildMode.MENU:
            return
        self.menu_index = (self.menu_index + 1) % len(BUILD_KINDS)
        self.selected = BUILD_KINDS[self.menu_index]

    def enter_place(self) -> None:
        if self.mode != BuildMode.MENU:
            return
        self.mode = BuildMode.PLACE
        self.cable_chain.clear()

    def cancel_build(self) -> None:
        self.mode = BuildMode.NONE
        self.cable_chain.clear()

    def back_to_menu(self) -> None:
        self.cancel_build()

    def can_place_tile(self, world: World, x: int, y: int, kind: BuildKind | None = None) -> bool:
        if not world.in_bounds(x, y):
            return False
        if not world.explored[world.idx(x, y)]:
            return False
        if (x, y) in world.module_cells or (x, y) in world.cables:
            return False
        tile = Tile(world.tiles[world.idx(x, y)])
        if kind == BuildKind.CABLE:
            return tile == Tile.GROUND
        if kind is None:
            return tile == Tile.GROUND
        mod_kind = BUILD_TO_MODULE[kind]
        defn = module_def(mod_kind)
        if defn.placement_deposit == Deposit.WATER:
            return world.patch_has_deposit(x, y, Deposit.WATER)
        if defn.placement_deposit == Deposit.MINERAL:
            return tile == Tile.GROUND and world.patch_has_deposit(x, y, Deposit.MINERAL)
        return tile == Tile.GROUND

    def _can_extend_cable(self, world: World, x: int, y: int, connected: set[tuple[int, int]]) -> bool:
        if not self.can_place_tile(world, x, y, BuildKind.CABLE):
            return False
        if (x, y) in self.cable_chain:
            return False
        if self.cable_chain:
            px, py = self.cable_chain[-1]
            if abs(px - x) + abs(py - y) != 1:
                return False
            return True
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            if (x + dx, y + dy) in connected or (x + dx, y + dy) in self.cable_chain:
                return True
        return False

    def preview_valid(self, world: World, stock: Stockpile, x: int, y: int) -> bool:
        connected = get_connected(world)
        if self.selected == BuildKind.CABLE:
            return self._can_extend_cable(world, x, y, connected)
        return self.can_place_tile(world, x, y, self.selected) and stock.can_afford(
            kind_cost(self.selected)
        )

    def try_place(self, world: World, stock: Stockpile, x: int, y: int) -> bool:
        connected = get_connected(world)
        if self.selected == BuildKind.CABLE:
            if not self._can_extend_cable(world, x, y, connected):
                return False
            if not stock.spend(CABLE_COST):
                return False
            world.cables.add((x, y))
            self.cable_chain.append((x, y))
            on_cable_added(world, x, y)
            invalidate_network_cache(world)
            self._refresh_connection_states(world, get_connected(world))
            return True

        if not self.can_place_tile(world, x, y, self.selected):
            return False
        cost = kind_cost(self.selected)
        if not stock.spend(cost):
            return False

        mod_kind = module_kind_for(self.selected)
        build_days = kind_build_days(self.selected)
        tile_connected = is_adjacent_to_network(x, y, connected)

        mod = Module(
            kind=mod_kind,
            x=x,
            y=y,
            state=ModuleState.BUILDING if tile_connected else ModuleState.WAITING,
            build_progress=0.0,
            build_total=build_days,
        )
        world.modules.append(mod)
        world.module_cells[(x, y)] = mod
        invalidate_network_cache(world)
        return True

    def _refresh_connection_states(self, world: World, connected: set[tuple[int, int]]) -> None:
        for mod in world.modules:
            if mod.kind == ModuleKind.HABITAT:
                continue
            prev = mod.state
            if mod.state == ModuleState.WAITING and is_adjacent_to_network(mod.x, mod.y, connected):
                mod.state = ModuleState.BUILDING
            elif mod.state == ModuleState.BUILDING and not is_adjacent_to_network(mod.x, mod.y, connected):
                mod.state = ModuleState.WAITING
            elif mod.state in (ModuleState.ONLINE, ModuleState.OFFLINE):
                mod.state = ModuleState.ONLINE if (mod.x, mod.y) in connected else ModuleState.OFFLINE
            if prev == mod.state:
                continue
            was_online = prev == ModuleState.ONLINE
            is_online = mod.state == ModuleState.ONLINE
            if prev in (ModuleState.BUILDING, ModuleState.WAITING) and mod.state in (
                ModuleState.ONLINE,
                ModuleState.OFFLINE,
            ):
                on_module_built(world, mod)
            elif was_online != is_online:
                on_module_online_changed(world, mod, was_online, is_online)

    def update_sites(self, world: World, dt_days: float) -> None:
        connected = get_connected(world)
        for mod in world.modules:
            if mod.kind == ModuleKind.HABITAT:
                continue
            if mod.state == ModuleState.BUILDING and mod.build_total > 0:
                mod.build_progress = min(mod.build_total, mod.build_progress + dt_days)
                if mod.build_progress >= mod.build_total:
                    mod.state = ModuleState.ONLINE if (mod.x, mod.y) in connected else ModuleState.OFFLINE
                    on_module_built(world, mod)
        self._refresh_connection_states(world, connected)
