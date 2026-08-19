"""Conectividad de red desde el hábitat."""

from __future__ import annotations

from collections import deque

from config import HABITAT_X, HABITAT_Y
from world import World

_NEIGHBORS = ((0, -1), (0, 1), (-1, 0), (1, 0))


def compute_connected(world: World) -> set[tuple[int, int]]:
    """Tiles de módulo o cable alcanzables desde el hábitat."""
    start = (HABITAT_X, HABITAT_Y)
    if start not in world.module_cells:
        return set()

    seen: set[tuple[int, int]] = {start}
    queue: deque[tuple[int, int]] = deque([start])

    while queue:
        x, y = queue.popleft()
        for dx, dy in _NEIGHBORS:
            nx, ny = x + dx, y + dy
            if not world.in_bounds(nx, ny):
                continue
            if (nx, ny) in seen:
                continue
            if (nx, ny) in world.cables or (nx, ny) in world.module_cells:
                seen.add((nx, ny))
                queue.append((nx, ny))

    return seen


def is_connected(world: World, x: int, y: int, connected: set[tuple[int, int]] | None = None) -> bool:
    if connected is None:
        connected = compute_connected(world)
    return (x, y) in connected


def is_adjacent_to_network(x: int, y: int, connected: set[tuple[int, int]]) -> bool:
    """Módulo alcanzable: tile en red o adyacente a ella."""
    if (x, y) in connected:
        return True
    for dx, dy in _NEIGHBORS:
        if (x + dx, y + dy) in connected:
            return True
    return False
