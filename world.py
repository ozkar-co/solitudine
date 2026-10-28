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
    STARTER_DEP_MINERAL_R,
    STARTER_DEP_MINERAL_X,
    STARTER_DEP_MINERAL_Y,
    STARTER_DEPOSIT_MULTIPLIER,
    DEPOSIT_MINERAL_PER_TILE,
    DEPOSIT_WATER_PER_TILE,
    EXTRACTOR_PATCH_RADIUS,
    MODULE_BUFFER_CAP,
    MODULES_NO_BUFFER,
    STARTER_DEP_WATER_R,
    STARTER_DEP_WATER_X,
    STARTER_DEP_WATER_Y,
    STARTER_WATER_R,
    STARTER_WATER_X,
    STARTER_WATER_Y,
    SURFACE_WATER_PER_TILE,
    WORLD_SEED,
    WORLD_SIZE,
)
from module_kind import ModuleKind


class Tile(IntEnum):
    GROUND = 0
    WATER = 1
    ROCK = 2


class Deposit(IntEnum):
    NONE = 0
    WATER = 1
    MINERAL = 2


class ModuleState(IntEnum):
    WAITING = 0
    BUILDING = 1
    OFFLINE = 2
    ONLINE = 3


@dataclass
class Module:
    kind: ModuleKind
    x: int
    y: int
    state: ModuleState = ModuleState.ONLINE
    build_progress: float = 0.0
    build_total: float = 0.0
    buffer: float = 0.0
    buffer_cap: float = 0.0
    shadow_stamped: bool = False
    clear_active: bool = False

    def __post_init__(self) -> None:
        if self.buffer_cap == 0.0 and self.kind.value not in MODULES_NO_BUFFER:
            self.buffer_cap = MODULE_BUFFER_CAP


@dataclass
class World:
    tiles: list[int]
    deposits: list[int]
    deposit_amounts: list[float]
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
    explored_version: int = 0
    _network_cache: set[tuple[int, int]] | None = field(default=None, repr=False, compare=False)

    def invalidate_network_cache(self) -> None:
        self._network_cache = None

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

    def deposit_amount_at(self, x: int, y: int) -> float:
        if not self.in_bounds(x, y):
            return 0.0
        return self.deposit_amounts[self.idx(x, y)]

    def extract_from_patch(self, cx: int, cy: int, kind: Deposit, amount: float) -> float:
        """Extrae hasta amount desde 3×3; agota depósitos y lagos."""
        if amount <= 0:
            return 0.0
        extracted = 0.0
        r = EXTRACTOR_PATCH_RADIUS
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if extracted >= amount:
                    break
                x, y = cx + dx, cy + dy
                if not self.in_bounds(x, y):
                    continue
                i = self.idx(x, y)
                need = amount - extracted
                if kind == Deposit.WATER:
                    if Tile(self.tiles[i]) == Tile.WATER:
                        available = self.deposit_amounts[i]
                        if available <= 0:
                            continue
                        take = min(available, need)
                        self.deposit_amounts[i] -= take
                        extracted += take
                        if self.deposit_amounts[i] <= 0:
                            self.tiles[i] = Tile.GROUND
                        continue
                    if Deposit(self.deposits[i]) != Deposit.WATER:
                        continue
                elif Deposit(self.deposits[i]) != kind:
                    continue
                available = self.deposit_amounts[i]
                if available <= 0:
                    continue
                take = min(available, need)
                self.deposit_amounts[i] -= take
                extracted += take
                if self.deposit_amounts[i] <= 0:
                    self.deposits[i] = Deposit.NONE
        return extracted

    def patch_deposit_total(self, cx: int, cy: int, kind: Deposit) -> float:
        total = 0.0
        r = EXTRACTOR_PATCH_RADIUS
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                x, y = cx + dx, cy + dy
                if not self.in_bounds(x, y):
                    continue
                i = self.idx(x, y)
                if kind == Deposit.WATER:
                    if Tile(self.tiles[i]) == Tile.WATER:
                        total += self.deposit_amounts[i]
                    elif Deposit(self.deposits[i]) == Deposit.WATER:
                        total += self.deposit_amounts[i]
                elif Deposit(self.deposits[i]) == kind:
                    total += self.deposit_amounts[i]
        return total

    def patch_has_deposit(self, cx: int, cy: int, kind: Deposit) -> bool:
        r = EXTRACTOR_PATCH_RADIUS
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                x, y = cx + dx, cy + dy
                if not self.in_bounds(x, y):
                    continue
                i = self.idx(x, y)
                if kind == Deposit.WATER:
                    if Tile(self.tiles[i]) == Tile.WATER and self.deposit_amounts[i] > 0:
                        return True
                    if Deposit(self.deposits[i]) == Deposit.WATER and self.deposit_amounts[i] > 0:
                        return True
                elif Deposit(self.deposits[i]) == kind and self.deposit_amounts[i] > 0:
                    return True
        return False

    def module_at(self, x: int, y: int) -> Module | None:
        return self.module_cells.get((x, y))

    def radar_scan_at(self, x: int, y: int) -> bool:
        r2 = RADAR_VISION_CLEAR * RADAR_VISION_CLEAR
        for mod in self.modules:
            if mod.kind == ModuleKind.RADAR and mod.state == ModuleState.ONLINE:
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
                    i = self.idx(x, y)
                    was_explored = mask[i]
                    mask[i] = 1
                    if track and not was_explored:
                        self._touch_explored(x, y)
                        self.explored_version += 1


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
    deposit_amounts = [0.0] * n
    explored = bytearray(n)
    visible = bytearray(n)

    for _ in range(55):
        _paint_blob(
            tiles,
            deposit_amounts,
            size,
            rng,
            Tile.WATER,
            blob_r=rng.randint(4, 11),
            amount_per_tile=SURFACE_WATER_PER_TILE,
        )
    for _ in range(40):
        _paint_blob(tiles, deposit_amounts, size, rng, Tile.ROCK, blob_r=rng.randint(3, 8))
    for _ in range(45):
        _paint_deposit(deposits, deposit_amounts, tiles, size, rng, Deposit.WATER, blob_r=rng.randint(3, 9))
    for _ in range(35):
        _paint_deposit(deposits, deposit_amounts, tiles, size, rng, Deposit.MINERAL, blob_r=rng.randint(3, 8))

    _guarantee_starter_patches(tiles, deposits, deposit_amounts, size)

    from vision import init_habitat, make_visible_count

    world = World(
        tiles=tiles,
        deposits=deposits,
        deposit_amounts=deposit_amounts,
        explored=explored,
        visible=visible,
        visible_count=make_visible_count(n),
        size=size,
    )
    hab = Module(ModuleKind.HABITAT, HABITAT_X, HABITAT_Y)
    world.modules.append(hab)
    world.module_cells[(HABITAT_X, HABITAT_Y)] = hab
    tiles[world.idx(HABITAT_X, HABITAT_Y)] = Tile.GROUND

    init_habitat(world, hab)
    return world


def _paint_blob(
    tiles: list[int],
    deposit_amounts: list[float],
    size: int,
    rng: random.Random,
    kind: Tile,
    blob_r: int,
    *,
    amount_per_tile: float = 0.0,
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
                if kind == Tile.WATER and amount_per_tile > 0:
                    deposit_amounts[i] = amount_per_tile * rng.uniform(0.7, 1.3)


def _paint_disc_tile(
    tiles: list[int],
    deposit_amounts: list[float],
    size: int,
    cx: int,
    cy: int,
    radius: int,
    kind: Tile,
    *,
    amount_per_tile: float = 0.0,
) -> None:
    r2 = radius * radius
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            if dx * dx + dy * dy > r2:
                continue
            x, y = cx + dx, cy + dy
            if not (0 <= x < size and 0 <= y < size):
                continue
            i = y * size + x
            if tiles[i] != Tile.ROCK:
                tiles[i] = kind
                if kind == Tile.WATER and amount_per_tile > 0:
                    deposit_amounts[i] = amount_per_tile


def _paint_disc_deposit(
    deposits: list[int],
    deposit_amounts: list[float],
    tiles: list[int],
    size: int,
    cx: int,
    cy: int,
    radius: int,
    kind: Deposit,
    *,
    amount_per_tile: float,
) -> None:
    r2 = radius * radius
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            if dx * dx + dy * dy > r2:
                continue
            x, y = cx + dx, cy + dy
            if not (0 <= x < size and 0 <= y < size):
                continue
            i = y * size + x
            if tiles[i] == Tile.GROUND:
                deposits[i] = kind
                deposit_amounts[i] = amount_per_tile


def _guarantee_starter_patches(
    tiles: list[int],
    deposits: list[int],
    deposit_amounts: list[float],
    size: int,
) -> None:
    """Reservas pequeñas cerca del hábitat para arrancar la partida."""
    wx = HABITAT_X + STARTER_WATER_X
    wy = HABITAT_Y + STARTER_WATER_Y
    _paint_disc_tile(
        tiles,
        deposit_amounts,
        size,
        wx,
        wy,
        STARTER_WATER_R,
        Tile.WATER,
        amount_per_tile=SURFACE_WATER_PER_TILE * STARTER_DEPOSIT_MULTIPLIER,
    )
    starter_amt = DEPOSIT_WATER_PER_TILE * STARTER_DEPOSIT_MULTIPLIER
    mineral_amt = DEPOSIT_MINERAL_PER_TILE * STARTER_DEPOSIT_MULTIPLIER
    _paint_disc_deposit(
        deposits,
        deposit_amounts,
        tiles,
        size,
        HABITAT_X + STARTER_DEP_WATER_X,
        HABITAT_Y + STARTER_DEP_WATER_Y,
        STARTER_DEP_WATER_R,
        Deposit.WATER,
        amount_per_tile=starter_amt,
    )
    _paint_disc_deposit(
        deposits,
        deposit_amounts,
        tiles,
        size,
        HABITAT_X + STARTER_DEP_MINERAL_X,
        HABITAT_Y + STARTER_DEP_MINERAL_Y,
        STARTER_DEP_MINERAL_R,
        Deposit.MINERAL,
        amount_per_tile=mineral_amt,
    )
    tiles[HABITAT_Y * size + HABITAT_X] = Tile.GROUND
    hi = HABITAT_Y * size + HABITAT_X
    deposits[hi] = Deposit.NONE
    deposit_amounts[hi] = 0.0


def _paint_deposit(
    deposits: list[int],
    deposit_amounts: list[float],
    tiles: list[int],
    size: int,
    rng: random.Random,
    kind: Deposit,
    blob_r: int,
) -> None:
    cx = rng.randint(blob_r, size - blob_r - 1)
    cy = rng.randint(blob_r, size - blob_r - 1)
    per_tile = DEPOSIT_WATER_PER_TILE if kind == Deposit.WATER else DEPOSIT_MINERAL_PER_TILE
    r2 = blob_r * blob_r
    for dy in range(-blob_r, blob_r + 1):
        for dx in range(-blob_r, blob_r + 1):
            if dx * dx + dy * dy > r2:
                continue
            x, y = cx + dx, cy + dy
            i = y * size + x
            if tiles[i] == Tile.GROUND and deposits[i] == Deposit.NONE:
                deposits[i] = kind
                deposit_amounts[i] = per_tile * rng.uniform(0.7, 1.3)
