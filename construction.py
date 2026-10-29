"""Modos y acciones de construcción."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from module_defs import CABLE_COST, ModuleKind, module_def
from network import get_connected, invalidate_network_cache, is_adjacent_to_network
from resources import Cost, ResourcePool
from tech_defs import tech_for_module
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
    LAMP = auto()
    LABORATORY = auto()
    ELECTROLYZER = auto()
    CONDENSER = auto()
    RECYCLER = auto()


BUILD_CATEGORIES: tuple[tuple[str, tuple[BuildKind, ...]], ...] = (
    ("category.energy", (BuildKind.SOLAR,)),
    ("category.extraction", (BuildKind.EXTRACTOR, BuildKind.MINE)),
    (
        "category.support",
        (BuildKind.GREENHOUSE, BuildKind.LAMP, BuildKind.ELECTROLYZER, BuildKind.CONDENSER),
    ),
    (
        "category.logistics",
        (BuildKind.CABLE, BuildKind.FABRICATOR, BuildKind.STORAGE, BuildKind.RECYCLER),
    ),
    ("category.science", (BuildKind.RADAR, BuildKind.LABORATORY)),
)

BUILD_CATEGORIES = tuple((key, kinds) for key, kinds in BUILD_CATEGORIES if kinds)
BUILD_KINDS = tuple(kind for _key, kinds in BUILD_CATEGORIES for kind in kinds)


class BuildMode(Enum):
    NONE = auto()
    MENU = auto()
    PLACE = auto()


class BuildPreview(Enum):
    OK = "ok"
    OUT_OF_BOUNDS = "out_of_bounds"
    UNEXPLORED = "unexplored"
    OCCUPIED = "occupied"
    RUIN = "ruin"
    BAD_TERRAIN = "bad_terrain"
    NO_WATER_DEPOSIT = "no_water_deposit"
    NO_MINERAL_DEPOSIT = "no_mineral_deposit"
    NO_RESOURCES = "no_resources"
    NO_NETWORK = "no_network"
    CABLE_NOT_CHAIN = "cable_not_chain"


def preview_locale_key(preview: BuildPreview) -> str:
    if preview == BuildPreview.OK:
        return "build.preview_ok"
    return f"build.err.{preview.value}"


BUILD_TO_MODULE: dict[BuildKind, ModuleKind] = {
    BuildKind.SOLAR: ModuleKind.SOLAR,
    BuildKind.RADAR: ModuleKind.RADAR,
    BuildKind.EXTRACTOR: ModuleKind.EXTRACTOR,
    BuildKind.GREENHOUSE: ModuleKind.GREENHOUSE,
    BuildKind.MINE: ModuleKind.MINE,
    BuildKind.FABRICATOR: ModuleKind.FABRICATOR,
    BuildKind.STORAGE: ModuleKind.STORAGE,
    BuildKind.LAMP: ModuleKind.LAMP,
    BuildKind.LABORATORY: ModuleKind.LABORATORY,
    BuildKind.ELECTROLYZER: ModuleKind.ELECTROLYZER,
    BuildKind.CONDENSER: ModuleKind.CONDENSER,
    BuildKind.RECYCLER: ModuleKind.RECYCLER,
}


def kind_cost(kind: BuildKind) -> Cost:
    if kind == BuildKind.CABLE:
        return CABLE_COST
    return module_def(BUILD_TO_MODULE[kind]).cost


def kind_build_days(kind: BuildKind) -> float:
    if kind == BuildKind.CABLE:
        return 0.0
    return module_def(BUILD_TO_MODULE[kind]).build_days


def module_kind_for(build: BuildKind) -> ModuleKind:
    return BUILD_TO_MODULE[build]


def kind_locked(build: BuildKind, unlocked: set[str]) -> bool:
    if build == BuildKind.CABLE:
        return False
    tech_id = tech_for_module(BUILD_TO_MODULE[build])
    return tech_id is not None and tech_id not in unlocked


@dataclass
class BuildController:
    mode: BuildMode = BuildMode.NONE
    selected: BuildKind = BuildKind.CABLE
    menu_category: int = 0
    menu_item: int = 0
    cable_chain: list[tuple[int, int]] = field(default_factory=list)

    def _current_kinds(self) -> tuple[BuildKind, ...]:
        return BUILD_CATEGORIES[self.menu_category][1]

    def _sync_selected(self) -> None:
        self.selected = self._current_kinds()[self.menu_item]

    def enter_menu(self) -> None:
        self.mode = BuildMode.MENU
        self.menu_category = 0
        self.menu_item = 0
        self._sync_selected()
        self.cable_chain.clear()

    def exit_menu(self) -> None:
        self.mode = BuildMode.NONE
        self.cable_chain.clear()

    def menu_up(self) -> None:
        if self.mode != BuildMode.MENU:
            return
        self.menu_item = (self.menu_item - 1) % len(self._current_kinds())
        self._sync_selected()

    def menu_down(self) -> None:
        if self.mode != BuildMode.MENU:
            return
        self.menu_item = (self.menu_item + 1) % len(self._current_kinds())
        self._sync_selected()

    def menu_left(self) -> None:
        if self.mode != BuildMode.MENU:
            return
        self.menu_category = (self.menu_category - 1) % len(BUILD_CATEGORIES)
        self.menu_item = 0
        self._sync_selected()

    def menu_right(self) -> None:
        if self.mode != BuildMode.MENU:
            return
        self.menu_category = (self.menu_category + 1) % len(BUILD_CATEGORIES)
        self.menu_item = 0
        self._sync_selected()

    def enter_place(self) -> None:
        if self.mode != BuildMode.MENU:
            return
        self.mode = BuildMode.PLACE
        self.cable_chain.clear()

    def cancel_build(self) -> None:
        self.mode = BuildMode.NONE
        self.cable_chain.clear()

    def back_to_menu(self) -> None:
        if self.mode != BuildMode.PLACE:
            return
        self.mode = BuildMode.MENU
        self.cable_chain.clear()

    def _tile_preview(self, world: World, x: int, y: int, kind: BuildKind) -> BuildPreview:
        if not world.in_bounds(x, y):
            return BuildPreview.OUT_OF_BOUNDS
        if not world.explored[world.idx(x, y)]:
            return BuildPreview.UNEXPLORED
        if (x, y) in world.module_cells or (x, y) in world.cables:
            return BuildPreview.OCCUPIED
        if world.has_ruin(x, y):
            return BuildPreview.RUIN
        tile = Tile(world.tiles[world.idx(x, y)])
        if kind == BuildKind.CABLE:
            return BuildPreview.OK if tile == Tile.GROUND else BuildPreview.BAD_TERRAIN
        mod_kind = BUILD_TO_MODULE[kind]
        defn = module_def(mod_kind)
        if defn.placement_deposit == Deposit.WATER:
            return BuildPreview.OK if world.patch_has_deposit(x, y, Deposit.WATER) else BuildPreview.NO_WATER_DEPOSIT
        if defn.placement_deposit == Deposit.MINERAL:
            if tile != Tile.GROUND:
                return BuildPreview.BAD_TERRAIN
            return BuildPreview.OK if world.patch_has_deposit(x, y, Deposit.MINERAL) else BuildPreview.NO_MINERAL_DEPOSIT
        return BuildPreview.OK if tile == Tile.GROUND else BuildPreview.BAD_TERRAIN

    def can_place_tile(self, world: World, x: int, y: int, kind: BuildKind | None = None) -> bool:
        if kind is None:
            kind = self.selected
        return self._tile_preview(world, x, y, kind) == BuildPreview.OK

    def _cable_preview(self, world: World, x: int, y: int, connected: set[tuple[int, int]]) -> BuildPreview:
        tile_status = self._tile_preview(world, x, y, BuildKind.CABLE)
        if tile_status != BuildPreview.OK:
            return tile_status
        if (x, y) in self.cable_chain:
            return BuildPreview.OCCUPIED
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            nx, ny = x + dx, y + dy
            if (nx, ny) in connected or (nx, ny) in self.cable_chain:
                return BuildPreview.OK
        if self.cable_chain:
            return BuildPreview.CABLE_NOT_CHAIN
        return BuildPreview.NO_NETWORK

    def _can_extend_cable(self, world: World, x: int, y: int, connected: set[tuple[int, int]]) -> bool:
        return self._cable_preview(world, x, y, connected) == BuildPreview.OK

    def preview(self, world: World, resources: ResourcePool, x: int, y: int) -> BuildPreview:
        connected = get_connected(world)
        if self.selected == BuildKind.CABLE:
            preview = self._cable_preview(world, x, y, connected)
            if preview != BuildPreview.OK:
                return preview
            return (
                BuildPreview.OK
                if CABLE_COST.can_afford(resources)
                else BuildPreview.NO_RESOURCES
            )
        preview = self._tile_preview(world, x, y, self.selected)
        if preview != BuildPreview.OK:
            return preview
        return (
            BuildPreview.OK
            if kind_cost(self.selected).can_afford(resources)
            else BuildPreview.NO_RESOURCES
        )

    def preview_valid(self, world: World, resources: ResourcePool, x: int, y: int) -> bool:
        return self.preview(world, resources, x, y) == BuildPreview.OK

    def selected_locked(self, unlocked: set[str]) -> bool:
        return kind_locked(self.selected, unlocked)

    def try_place(
        self,
        world: World,
        resources: ResourcePool,
        x: int,
        y: int,
        unlocked: set[str] | None = None,
    ) -> bool:
        if unlocked is not None and self.selected_locked(unlocked):
            return False
        connected = get_connected(world)
        if self.selected == BuildKind.CABLE:
            if not self._can_extend_cable(world, x, y, connected):
                return False
            if not CABLE_COST.spend(resources):
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
        if not cost.spend(resources):
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
            cost_paid=cost,
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

    def refresh_network(self, world: World) -> None:
        invalidate_network_cache(world)
        self._refresh_connection_states(world, get_connected(world))

    def update_sites(self, world: World, dt_days: float, day: int = 0) -> None:
        connected = get_connected(world)
        for mod in world.modules:
            if mod.kind == ModuleKind.HABITAT:
                continue
            if mod.state == ModuleState.BUILDING and mod.build_total > 0:
                mod.build_progress = min(mod.build_total, mod.build_progress + dt_days)
                if mod.build_progress >= mod.build_total:
                    mod.state = ModuleState.ONLINE if (mod.x, mod.y) in connected else ModuleState.OFFLINE
                    mod.built_day = day
                    on_module_built(world, mod)
        self._refresh_connection_states(world, connected)
