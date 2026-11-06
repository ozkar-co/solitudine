"""Mapa, terreno, visibilidad y módulos."""

from __future__ import annotations

import math
import random
import secrets
import string
from array import array
from dataclasses import dataclass, field
from enum import IntEnum

from config import (
    DEPOSIT_COAL_PER_TILE,
    DEPOSIT_CRYSTAL_PER_TILE,
    INITIAL_VISION_RADIUS,
    RADAR_VISION_CLEAR,
    RUIN_GUARANTEED_SCRAP_MAX,
    RUIN_GUARANTEED_SCRAP_MIN,
    RUIN_MAX_PLACEMENT_TRIES,
    RUIN_PROCEDURAL,
    RUIN_SCRAP_MAX,
    RUIN_SCRAP_MIN,
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
    WORLD_CHUNK_SIZE,
    WORLD_SEED,
    WORLD_SIZE,
)
from module_kind import ModuleKind
from resources import Cost, ResourceId


class Tile(IntEnum):
    GROUND = 0
    WATER = 1
    ROCK = 2
    FOREST = 3
    SPROUT = 4


class Deposit(IntEnum):
    NONE = 0
    WATER = 1
    MINERAL = 2
    COAL = 3
    CRYSTAL = 4


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
    enabled: bool = True
    build_progress: float = 0.0
    build_total: float = 0.0
    buffer: float = 0.0
    buffer_cap: float = 0.0
    shadow_stamped: bool = False
    clear_active: bool = False
    built_day: int = 0
    cost_paid: Cost = field(default_factory=Cost.empty)
    fuel_resource: ResourceId | None = None

    def __post_init__(self) -> None:
        if self.buffer_cap == 0.0 and self.kind.value not in MODULES_NO_BUFFER:
            self.buffer_cap = MODULE_BUFFER_CAP


@dataclass
class World:
    tiles: bytearray
    deposits: bytearray
    deposit_amounts: array
    explored: bytearray
    visible: bytearray
    visible_count: array
    modules: list[Module] = field(default_factory=list)
    module_cells: dict[tuple[int, int], Module] = field(default_factory=dict)
    cables: set[tuple[int, int]] = field(default_factory=set)
    ruins: dict[tuple[int, int], float] = field(default_factory=dict)
    size: int = WORLD_SIZE
    seed: str = WORLD_SEED
    expl_min_x: int = WORLD_SIZE
    expl_min_y: int = WORLD_SIZE
    expl_max_x: int = 0
    expl_max_y: int = 0
    explored_version: int = 0
    _network_cache: set[tuple[int, int]] | None = field(default=None, repr=False, compare=False)

    @property
    def habitat_x(self) -> int:
        return self.size // 2

    @property
    def habitat_y(self) -> int:
        return self.size // 2

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

    def has_ruin(self, x: int, y: int) -> bool:
        return self.ruins.get((x, y), 0.0) > 0.0

    def ruin_amount(self, x: int, y: int) -> float:
        return self.ruins.get((x, y), 0.0)

    def add_ruin(self, x: int, y: int, amount: float) -> None:
        if amount <= 0.0 or not self.in_bounds(x, y):
            return
        self.ruins[(x, y)] = self.ruins.get((x, y), 0.0) + amount

    def take_ruin(self, x: int, y: int, amount: float) -> float:
        available = self.ruin_amount(x, y)
        taken = min(available, max(0.0, amount))
        if taken <= 0.0:
            return 0.0
        remaining = available - taken
        if remaining <= 0.0:
            self.ruins.pop((x, y), None)
        else:
            self.ruins[(x, y)] = remaining
        return taken

    def radar_scan_at(self, x: int, y: int) -> bool:
        r2 = RADAR_VISION_CLEAR * RADAR_VISION_CLEAR
        for mod in self.modules:
            if mod.kind == ModuleKind.RADAR and mod.state == ModuleState.ONLINE:
                if (x - mod.x) ** 2 + (y - mod.y) ** 2 <= r2:
                    return True
        return False

    def camera_bounds(self, margin: int) -> tuple[int, int, int, int]:
        # La cámara puede llegar a cualquier borde del mapa; la niebla sigue
        # ocultando lo no explorado.
        return (0, 0, self.size - 1, self.size - 1)

    def cursor_bounds(self, margin: int) -> tuple[int, int, int, int]:
        if self.expl_max_x < self.expl_min_x:
            r = INITIAL_VISION_RADIUS + margin
            hx, hy = self.habitat_x, self.habitat_y
            return (hx - r, hy - r, hx + r, hy + r)
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


def new_seed() -> str:
    """Nombre/semilla de mapa: 3 letras + 3 números (p. ej. NEP-325)."""
    letters = "".join(secrets.choice(string.ascii_uppercase) for _ in range(3))
    digits = "".join(secrets.choice(string.digits) for _ in range(3))
    return f"{letters}-{digits}"


def _seed_int(text: str) -> int:
    h = 0
    for ch in text:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    return h


def generate_world(seed: str = WORLD_SEED, size: int = WORLD_SIZE) -> World:
    if size < 64:
        raise ValueError("El mapa debe tener al menos 64 tiles por lado")
    rng = random.Random(_seed_int(f"{seed}:{size}"))
    n = size * size
    tiles = bytearray(n)
    deposits = bytearray(n)
    deposit_amounts = array("f", [0.0]) * n
    explored = bytearray(n)
    visible = bytearray(n)
    ruins: dict[tuple[int, int], float] = {}

    _generate_chunk_features(tiles, deposits, deposit_amounts, size, rng)
    _guarantee_starter_patches(tiles, deposits, deposit_amounts, size)
    _guarantee_near_forest(tiles, deposits, deposit_amounts, size, rng)
    _guarantee_edge_coal(tiles, deposits, deposit_amounts, size, rng)
    _guarantee_crystal_cluster(tiles, deposits, deposit_amounts, size, rng)
    _generate_ruins(ruins, tiles, deposits, deposit_amounts, size, rng)

    from vision import init_habitat, make_visible_count

    world = World(
        tiles=tiles,
        deposits=deposits,
        deposit_amounts=deposit_amounts,
        explored=explored,
        visible=visible,
        visible_count=make_visible_count(n),
        ruins=ruins,
        size=size,
        seed=seed,
    )
    hx, hy = world.habitat_x, world.habitat_y
    hab = Module(ModuleKind.HABITAT, hx, hy)
    world.modules.append(hab)
    world.module_cells[(hx, hy)] = hab
    hi = world.idx(hx, hy)
    tiles[hi] = Tile.GROUND
    deposits[hi] = Deposit.NONE
    deposit_amounts[hi] = 0.0

    init_habitat(world, hab)
    return world


def _clamp(value: float, low: int, high: int) -> int:
    return max(low, min(high, int(value)))


def _distance_ratio(x: int, y: int, size: int) -> float:
    hx = hy = size // 2
    max_d = math.hypot(hx, hy)
    if max_d <= 0.0:
        return 0.0
    return min(1.0, math.hypot(x - hx, y - hy) / max_d)


def _generate_chunk_features(
    tiles: bytearray,
    deposits: bytearray,
    deposit_amounts: array,
    size: int,
    rng: random.Random,
) -> None:
    chunk = WORLD_CHUNK_SIZE
    for cy0 in range(0, size, chunk):
        for cx0 in range(0, size, chunk):
            jitter = max(1, chunk // 3)
            cx = _clamp(cx0 + chunk // 2 + rng.randint(-jitter, jitter), 0, size - 1)
            cy = _clamp(cy0 + chunk // 2 + rng.randint(-jitter, jitter), 0, size - 1)
            d = _distance_ratio(cx, cy, size)

            if rng.random() < 0.20 + 0.05 * d:
                _paint_blob_at(
                    tiles,
                    deposit_amounts,
                    size,
                    rng,
                    Tile.WATER,
                    cx,
                    cy,
                    rng.randint(4, 11),
                    amount_per_tile=SURFACE_WATER_PER_TILE,
                )
            if rng.random() < 0.15 + 0.05 * d:
                _paint_blob_at(
                    tiles,
                    deposit_amounts,
                    size,
                    rng,
                    Tile.ROCK,
                    cx,
                    cy,
                    rng.randint(3, 8),
                )
            if rng.random() < 0.35 + 0.30 * d:
                _paint_deposit_at(
                    deposits,
                    deposit_amounts,
                    tiles,
                    size,
                    rng,
                    Deposit.WATER,
                    cx,
                    cy,
                    rng.randint(3, 9),
                )
            if rng.random() < 0.30 + 0.35 * d:
                _paint_deposit_at(
                    deposits,
                    deposit_amounts,
                    tiles,
                    size,
                    rng,
                    Deposit.MINERAL,
                    cx,
                    cy,
                    rng.randint(3, 8),
                )
            if rng.random() < 0.15 + 0.20 * d:
                _paint_forest(
                    tiles,
                    deposits,
                    size,
                    rng,
                    cx,
                    cy,
                    rng.randint(2, 4),
                )
            if rng.random() < 0.015 + 0.035 * d:
                _paint_coal_vein(tiles, deposits, deposit_amounts, size, rng, cx, cy, rng.randint(4, 10))
            if rng.random() < 0.004 + 0.020 * d * d:
                _paint_crystal_cluster(tiles, deposits, deposit_amounts, size, rng, cx, cy)


def _paint_blob_at(
    tiles: bytearray,
    deposit_amounts: array,
    size: int,
    rng: random.Random,
    kind: Tile,
    cx: int,
    cy: int,
    blob_r: int,
    *,
    amount_per_tile: float = 0.0,
) -> None:
    r2 = blob_r * blob_r
    for dy in range(-blob_r, blob_r + 1):
        for dx in range(-blob_r, blob_r + 1):
            if dx * dx + dy * dy > r2:
                continue
            x, y = cx + dx, cy + dy
            if not (0 <= x < size and 0 <= y < size):
                continue
            i = y * size + x
            if tiles[i] == Tile.GROUND:
                tiles[i] = kind
                if kind == Tile.WATER and amount_per_tile > 0:
                    deposit_amounts[i] = amount_per_tile * rng.uniform(0.7, 1.3)


def _paint_deposit_at(
    deposits: bytearray,
    deposit_amounts: array,
    tiles: bytearray,
    size: int,
    rng: random.Random,
    kind: Deposit,
    cx: int,
    cy: int,
    blob_r: int,
) -> None:
    per_tile = {
        Deposit.WATER: DEPOSIT_WATER_PER_TILE,
        Deposit.MINERAL: DEPOSIT_MINERAL_PER_TILE,
        Deposit.COAL: DEPOSIT_COAL_PER_TILE,
        Deposit.CRYSTAL: DEPOSIT_CRYSTAL_PER_TILE,
    }.get(kind, 0.0)
    r2 = blob_r * blob_r
    for dy in range(-blob_r, blob_r + 1):
        for dx in range(-blob_r, blob_r + 1):
            if dx * dx + dy * dy > r2:
                continue
            x, y = cx + dx, cy + dy
            if not (0 <= x < size and 0 <= y < size):
                continue
            i = y * size + x
            if tiles[i] == Tile.GROUND and deposits[i] == Deposit.NONE:
                deposits[i] = kind
                deposit_amounts[i] = per_tile * rng.uniform(0.7, 1.3)


def _paint_forest(
    tiles: bytearray,
    deposits: bytearray,
    size: int,
    rng: random.Random,
    cx: int,
    cy: int,
    blob_r: int,
) -> None:
    r2 = blob_r * blob_r
    for dy in range(-blob_r, blob_r + 1):
        for dx in range(-blob_r, blob_r + 1):
            if dx * dx + dy * dy > r2:
                continue
            x, y = cx + dx, cy + dy
            if not (0 <= x < size and 0 <= y < size):
                continue
            i = y * size + x
            if tiles[i] == Tile.GROUND and deposits[i] == Deposit.NONE:
                tiles[i] = Tile.FOREST


def _paint_coal_vein(
    tiles: bytearray,
    deposits: bytearray,
    deposit_amounts: array,
    size: int,
    rng: random.Random,
    cx: int,
    cy: int,
    length: int,
) -> None:
    x, y = cx, cy
    for _ in range(length):
        if 0 <= x < size and 0 <= y < size:
            i = y * size + x
            if tiles[i] == Tile.GROUND and deposits[i] == Deposit.NONE:
                deposits[i] = Deposit.COAL
                deposit_amounts[i] = DEPOSIT_COAL_PER_TILE * rng.uniform(0.8, 1.2)
        x = _clamp(x + rng.choice((-1, 0, 1)), 0, size - 1)
        y = _clamp(y + rng.choice((-1, 0, 1)), 0, size - 1)


def _paint_crystal_cluster(
    tiles: bytearray,
    deposits: bytearray,
    deposit_amounts: array,
    size: int,
    rng: random.Random,
    cx: int,
    cy: int,
) -> None:
    count = rng.randint(4, 5) if rng.random() < 0.2 else rng.randint(2, 3)
    placed: list[tuple[int, int]] = []
    for _ in range(count * 30):
        if len(placed) >= count:
            break
        x = cx + rng.randint(-4, 4)
        y = cy + rng.randint(-4, 4)
        if not (0 <= x < size and 0 <= y < size):
            continue
        if max(abs(x - cx), abs(y - cy)) < 2:
            continue
        if any(max(abs(x - px), abs(y - py)) < 2 for px, py in placed):
            continue
        i = y * size + x
        if tiles[i] != Tile.GROUND or deposits[i] != Deposit.NONE:
            continue
        placed.append((x, y))
        deposits[i] = Deposit.CRYSTAL
        deposit_amounts[i] = DEPOSIT_CRYSTAL_PER_TILE * rng.uniform(0.8, 1.2)


def _find_ground_near(
    tiles: bytearray,
    deposits: bytearray,
    size: int,
    rng: random.Random,
    radius_min: int,
    radius_max: int,
) -> tuple[int, int] | None:
    hx = hy = size // 2
    for _ in range(240):
        angle = rng.uniform(0.0, math.tau)
        radius = rng.uniform(radius_min, radius_max)
        x = int(hx + math.cos(angle) * radius)
        y = int(hy + math.sin(angle) * radius)
        if not (0 <= x < size and 0 <= y < size):
            continue
        i = y * size + x
        if tiles[i] == Tile.GROUND and deposits[i] == Deposit.NONE:
            return x, y
    return None


def _guarantee_near_forest(
    tiles: bytearray,
    deposits: bytearray,
    deposit_amounts: array,
    size: int,
    rng: random.Random,
) -> None:
    spot = _find_ground_near(tiles, deposits, size, rng, 8, 14)
    if spot is None:
        return
    cx, cy = spot
    _paint_forest(tiles, deposits, size, rng, cx, cy, rng.randint(2, 3))


def _guarantee_edge_coal(
    tiles: bytearray,
    deposits: bytearray,
    deposit_amounts: array,
    size: int,
    rng: random.Random,
) -> None:
    spot = _find_ground_near(tiles, deposits, size, rng, INITIAL_VISION_RADIUS + 4, INITIAL_VISION_RADIUS + 10)
    if spot is None:
        return
    x, y = spot
    i = y * size + x
    deposits[i] = Deposit.COAL
    deposit_amounts[i] = DEPOSIT_COAL_PER_TILE


def _guarantee_crystal_cluster(
    tiles: bytearray,
    deposits: bytearray,
    deposit_amounts: array,
    size: int,
    rng: random.Random,
) -> None:
    max_radius = int(math.hypot(size // 2, size // 2))
    low = max(1, int(max_radius * 0.65))
    high = max(low + 1, int(max_radius * 0.85))
    spot = _find_ground_near(tiles, deposits, size, rng, low, high)
    if spot is None:
        return
    _paint_crystal_cluster(tiles, deposits, deposit_amounts, size, rng, spot[0], spot[1])


def _paint_disc_tile(
    tiles: bytearray,
    deposits: bytearray,
    deposit_amounts: array,
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
                if kind == Tile.WATER:
                    deposits[i] = Deposit.NONE
                    deposit_amounts[i] = amount_per_tile if amount_per_tile > 0 else 0.0


def _paint_disc_deposit(
    deposits: bytearray,
    deposit_amounts: array,
    tiles: bytearray,
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


def _ruin_tile_ok(
    tiles: list[int],
    deposits: list[int],
    deposit_amounts: list[float],
    size: int,
    x: int,
    y: int,
) -> bool:
    if not (0 <= x < size and 0 <= y < size):
        return False
    if (x, y) == (size // 2, size // 2):
        return False
    i = y * size + x
    return tiles[i] == Tile.GROUND and deposits[i] == Deposit.NONE and deposit_amounts[i] <= 0.0


def _find_ruin_near(
    ruins: dict[tuple[int, int], float],
    tiles: list[int],
    deposits: list[int],
    deposit_amounts: list[float],
    size: int,
    cx: int,
    cy: int,
) -> tuple[int, int] | None:
    for radius in range(3, 14):
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if max(abs(dx), abs(dy)) != radius:
                    continue
                x, y = cx + dx, cy + dy
                if (x, y) not in ruins and _ruin_tile_ok(tiles, deposits, deposit_amounts, size, x, y):
                    return x, y
    return None


def _generate_ruins(
    ruins: dict[tuple[int, int], float],
    tiles: list[int],
    deposits: list[int],
    deposit_amounts: list[float],
    size: int,
    rng: random.Random,
) -> None:
    hx = hy = size // 2
    for _ in range(2):
        spot = _find_ruin_near(ruins, tiles, deposits, deposit_amounts, size, hx, hy)
        if spot is None:
            break
        ruins[spot] = rng.uniform(RUIN_GUARANTEED_SCRAP_MIN, RUIN_GUARANTEED_SCRAP_MAX)

    target = 2 + RUIN_PROCEDURAL
    for _ in range(RUIN_MAX_PLACEMENT_TRIES):
        if len(ruins) >= target:
            break
        x = rng.randrange(size)
        y = rng.randrange(size)
        if (x, y) in ruins or not _ruin_tile_ok(tiles, deposits, deposit_amounts, size, x, y):
            continue
        ruins[(x, y)] = rng.uniform(RUIN_SCRAP_MIN, RUIN_SCRAP_MAX)


def _guarantee_starter_patches(
    tiles: list[int],
    deposits: list[int],
    deposit_amounts: list[float],
    size: int,
) -> None:
    """Reservas pequeñas cerca del hábitat para arrancar la partida."""
    hx = hy = size // 2
    wx = hx + STARTER_WATER_X
    wy = hy + STARTER_WATER_Y
    _paint_disc_tile(
        tiles,
        deposits,
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
        hx + STARTER_DEP_WATER_X,
        hy + STARTER_DEP_WATER_Y,
        STARTER_DEP_WATER_R,
        Deposit.WATER,
        amount_per_tile=starter_amt,
    )
    _paint_disc_deposit(
        deposits,
        deposit_amounts,
        tiles,
        size,
        hx + STARTER_DEP_MINERAL_X,
        hy + STARTER_DEP_MINERAL_Y,
        STARTER_DEP_MINERAL_R,
        Deposit.MINERAL,
        amount_per_tile=mineral_amt,
    )
    hi = hy * size + hx
    tiles[hi] = Tile.GROUND
    deposits[hi] = Deposit.NONE
    deposit_amounts[hi] = 0.0
