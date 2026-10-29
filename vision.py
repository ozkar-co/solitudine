"""Visión incremental: neblina permanente + contadores de visión clara."""

from __future__ import annotations

from array import array

from config import (
    CABLE_SHADOW,
    CABLE_VISION,
    HABITAT_SHADOW_BORDER,
    INITIAL_VISION_RADIUS,
    RADAR_VISION_CLEAR,
    RADAR_VISION_FOG,
    SOLAR_VISION,
)


from module_defs import ModuleKind


def module_radii(kind: ModuleKind) -> tuple[int, int] | None:
    if kind == ModuleKind.HABITAT:
        return INITIAL_VISION_RADIUS, INITIAL_VISION_RADIUS + HABITAT_SHADOW_BORDER
    if kind == ModuleKind.SOLAR:
        return SOLAR_VISION, SOLAR_VISION
    if kind == ModuleKind.RADAR:
        return RADAR_VISION_CLEAR, RADAR_VISION_FOG
    return None


def _each_disc(world, cx: int, cy: int, radius: int):
    if radius <= 0:
        return
    r2 = radius * radius
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            if dx * dx + dy * dy > r2:
                continue
            x, y = cx + dx, cy + dy
            if world.in_bounds(x, y):
                yield x, y, world.idx(x, y)


def stamp_shadow(world, cx: int, cy: int, radius: int) -> None:
    """Neblina/explorado permanente — solo crece, nunca se borra."""
    world._stamp_disc(world.explored, cx, cy, radius)


def _adjust_clear(world, cx: int, cy: int, radius: int, delta: int) -> None:
    for _x, _y, i in _each_disc(world, cx, cy, radius):
        before = world.visible_count[i]
        after = before + delta
        if after < 0:
            after = 0
        world.visible_count[i] = after
        if before == 0 and after > 0:
            world.visible[i] = 1
        elif before > 0 and after == 0:
            world.visible[i] = 0


def activate_clear(world, cx: int, cy: int, radius: int) -> None:
    _adjust_clear(world, cx, cy, radius, 1)


def deactivate_clear(world, cx: int, cy: int, radius: int) -> None:
    _adjust_clear(world, cx, cy, radius, -1)


def ensure_module_shadow(world, mod) -> None:
    if mod.shadow_stamped:
        return
    radii = module_radii(mod.kind)
    if radii is None:
        return
    stamp_shadow(world, mod.x, mod.y, radii[1])
    mod.shadow_stamped = True


def set_module_clear(world, mod, active: bool) -> None:
    active = active and mod.enabled
    if mod.clear_active == active:
        return
    radii = module_radii(mod.kind)
    if radii is None:
        return
    if active:
        activate_clear(world, mod.x, mod.y, radii[0])
    else:
        deactivate_clear(world, mod.x, mod.y, radii[0])
    mod.clear_active = active


def on_module_built(world, mod) -> None:
    """Obra terminada: marca neblina y activa visión clara si está en línea."""
    from world import ModuleState

    ensure_module_shadow(world, mod)
    set_module_clear(world, mod, mod.state == ModuleState.ONLINE)


def on_module_online_changed(world, mod, was_online: bool, is_online: bool) -> None:
    if was_online == is_online:
        return
    if is_online:
        ensure_module_shadow(world, mod)
    set_module_clear(world, mod, is_online)


def on_cable_added(world, x: int, y: int) -> None:
    stamp_shadow(world, x, y, CABLE_SHADOW)
    activate_clear(world, x, y, CABLE_VISION)


def on_cable_removed(world, x: int, y: int) -> None:
    deactivate_clear(world, x, y, CABLE_VISION)


def on_module_removed(world, mod) -> None:
    set_module_clear(world, mod, False)


def init_habitat(world, mod) -> None:
    ensure_module_shadow(world, mod)
    set_module_clear(world, mod, True)


def make_visible_count(size: int) -> array:
    return array("H", [0]) * size
