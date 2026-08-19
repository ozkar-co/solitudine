"""Radios de visión y sombra por nodo — se fusionan en unión."""

from __future__ import annotations

from dataclasses import dataclass

from config import (
    CABLE_SHADOW,
    CABLE_VISION,
    HABITAT_SHADOW_BORDER,
    INITIAL_VISION_RADIUS,
    RADAR_VISION_CLEAR,
    RADAR_VISION_FOG,
    SOLAR_VISION,
)
from network import compute_connected


@dataclass(frozen=True)
class VisionSource:
    x: int
    y: int
    clear_r: int
    shadow_r: int


def _module_radii(kind: str) -> tuple[int, int] | None:
    if kind == "habitat":
        return INITIAL_VISION_RADIUS, INITIAL_VISION_RADIUS + HABITAT_SHADOW_BORDER
    if kind == "solar":
        return SOLAR_VISION, SOLAR_VISION
    if kind == "radar":
        return RADAR_VISION_CLEAR, RADAR_VISION_FOG
    return None


def collect_sources(world) -> list[VisionSource]:
    from world import ModuleState

    connected = compute_connected(world)
    sources: list[VisionSource] = []

    for mod in world.modules:
        radii = _module_radii(mod.kind)
        if radii is None:
            continue
        if mod.kind == "habitat" or mod.state == ModuleState.ONLINE:
            sources.append(VisionSource(mod.x, mod.y, radii[0], radii[1]))

    for x, y in world.cables:
        if (x, y) in connected:
            sources.append(VisionSource(x, y, CABLE_VISION, CABLE_SHADOW))

    return sources


def apply_vision(world) -> None:
    n = world.size * world.size
    world.visible[:] = b"\x00" * n
    for src in collect_sources(world):
        world._stamp_disc(world.explored, src.x, src.y, src.shadow_r)
        world._stamp_disc(world.visible, src.x, src.y, src.clear_r)
