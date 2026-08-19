"""Mapa, terreno, visibilidad y módulos."""

from __future__ import annotations

import random
from array import array
from dataclasses import dataclass, field
from enum import IntEnum

from config import (
    HABITAT_X,
    HABITAT_Y,
    INITIAL_VISION_RADIUS,
    RADAR_VISION_CLEAR,
    WORLD_SEED,
    WORLD_SIZE,
)


class Tile(IntEnum):
    GROUND = 0
    WATER = 1
    ROCK = 2


class Deposit(IntEnum):
    NONE = 0
    WATER = 1
    CARBON = 2


class ModuleState(IntEnum):
    WAITING = 0
    BUILDING = 1
    OFFLINE = 2
    ONLINE = 3


@dataclass
class Module:
    kind: str
    x: int
    y: int
    state: ModuleState = ModuleState.ONLINE
    build_progress: float = 0.0
    build_total: float = 0.0
    shadow_stamped: bool = False
    clear_active: bool = False


@dataclass
class World:
    tiles: list[int]
    deposits: list[int]
    explored: bytearray
    visible: bytearray
    visible_count: array
    modules: list[Module] = field(default_factory=list)
    module_cells: dict[tuple[int, int], Module] = field(default_factory=dict)
    cables: set[tuple[int, int]] = field(default_factory=set)
    size: int = WORLD_SIZE
    expl_min_x: int = WORLD_SIZE
    expl_min_y: int = WORLD_SIZE
    expl_max_x: int = 0
    expl_max_y: int = 0

    def idx(self, x: int, y: int) -> int:
        return y * self.size + x

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.size and 0 <= y < self.size

    def tile_at(self, x: int, y: int) -> Tile | None:
        if not self.in_bounds(x, y):
            return None
        if not self.explored[self.idx(x, y)]:
            return None
        return Tile(self.tiles[self.idx(x, y)])

    def deposit_at(self, x: int, y: int) -> Deposit | None:
        if not self.in_bounds(x, y):
            return None
        return Deposit(self.deposits[self.idx(x, y)])

    def module_at(self, x: int, y: int) -> Module | None:
        return self.module_cells.get((x, y))

    def radar_scan_at(self, x: int, y: int) -> bool:
        r2 = RADAR_VISION_CLEAR * RADAR_VISION_CLEAR
        for mod in self.modules:
            if mod.kind == "radar" and mod.state == ModuleState.ONLINE:
                if (x - mod.x) ** 2 + (y - mod.y) ** 2 <= r2:
                    return True
        return False

    def camera_bounds(self, margin: int) -> tuple[int, int, int, int]:
        if self.expl_max_x < self.expl_min_x:
            r = INITIAL_VISION_RADIUS + margin
            return (
                HABITAT_X - r,
                HABITAT_Y - r,
                HABITAT_X + r,
                HABITAT_Y + r,
            )
        return (
            max(0, self.expl_min_x - margin),
            max(0, self.expl_min_y - margin),
            min(self.size - 1, self.expl_max_x + margin),
            min(self.size - 1, self.expl_max_y + margin),
        )

    def _touch_explored(self, x: int, y: int) -> None:
        self.expl_min_x = min(self.expl_min_x, x)
        self.expl_min_y = min(self.expl_min_y, y)
        self.expl_max_x = max(self.expl_max_x, x)
        self.expl_max_y = max(self.expl_max_y, y)

    def _stamp_disc(self, mask: bytearray, cx: int, cy: int, radius: int) -> None:
        track = mask is self.explored
        if radius <= 0:
            return
        r2 = radius * radius
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx * dx + dy * dy > r2:
                    continue
                x, y = cx + dx, cy + dy
                if self.in_bounds(x, y):
                    mask[self.idx(x, y)] = 1
                    if track:
                        self._touch_explored(x, y)


def _seed_int(text: str) -> int:
    h = 0
    for ch in text:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    return h


def generate_world(seed: str = WORLD_SEED) -> World:
    rng = random.Random(_seed_int(seed))
    size = WORLD_SIZE
    n = size * size
    tiles = [Tile.GROUND] * n
    deposits = [Deposit.NONE] * n
    explored = bytearray(n)
    visible = bytearray(n)

    for _ in range(55):
        _paint_blob(tiles, size, rng, Tile.WATER, blob_r=rng.randint(4, 11))
    for _ in range(40):
        _paint_blob(tiles, size, rng, Tile.ROCK, blob_r=rng.randint(3, 8))
    for _ in range(45):
        _paint_deposit(deposits, tiles, size, rng, Deposit.WATER, blob_r=rng.randint(3, 9))
    for _ in range(35):
        _paint_deposit(deposits, tiles, size, rng, Deposit.CARBON, blob_r=rng.randint(3, 8))

    from vision import init_habitat, make_visible_count

    world = World(
        tiles=tiles,
        deposits=deposits,
        explored=explored,
        visible=visible,
        visible_count=make_visible_count(n),
        size=size,
    )
    hab = Module("habitat", HABITAT_X, HABITAT_Y)
    world.modules.append(hab)
    world.module_cells[(HABITAT_X, HABITAT_Y)] = hab
    tiles[world.idx(HABITAT_X, HABITAT_Y)] = Tile.GROUND

    init_habitat(world, hab)
    return world


def _paint_blob(
    tiles: list[int],
    size: int,
    rng: random.Random,
    kind: Tile,
    blob_r: int,
) -> None:
    cx = rng.randint(blob_r, size - blob_r - 1)
    cy = rng.randint(blob_r, size - blob_r - 1)
    r2 = blob_r * blob_r
    for dy in range(-blob_r, blob_r + 1):
        for dx in range(-blob_r, blob_r + 1):
            if dx * dx + dy * dy > r2:
                continue
            x, y = cx + dx, cy + dy
            i = y * size + x
            if tiles[i] == Tile.GROUND:
                tiles[i] = kind


def _paint_deposit(
    deposits: list[int],
    tiles: list[int],
    size: int,
    rng: random.Random,
    kind: Deposit,
    blob_r: int,
) -> None:
    cx = rng.randint(blob_r, size - blob_r - 1)
    cy = rng.randint(blob_r, size - blob_r - 1)
    r2 = blob_r * blob_r
    for dy in range(-blob_r, blob_r + 1):
        for dx in range(-blob_r, blob_r + 1):
            if dx * dx + dy * dy > r2:
                continue
            x, y = cx + dx, cy + dy
            i = y * size + x
            if tiles[i] == Tile.GROUND and deposits[i] == Deposit.NONE:
                deposits[i] = kind
