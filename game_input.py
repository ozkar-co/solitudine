"""Acciones del jugador por frame — extraído de game.py."""

from __future__ import annotations

from dataclasses import dataclass

from construction import BuildController, BuildKind, BuildMode
from gamepad import LJOY_DOWN, LJOY_LEFT, LJOY_RIGHT, LJOY_UP
from input_state import FrameInput, Input
from module_defs import module_active
from module_kind import ModuleKind
from network import get_connected
from simulation import Simulation
from ui import MapLayer
from vision import set_module_clear
from world import ModuleState, World


@dataclass
class FrameInputResult:
    layer: MapLayer
    select_x: int | None
    select_y: int | None
    reset_session: bool = False


def handle_frame_input(
    frame: FrameInput,
    inp: Input,
    sim: Simulation,
    world: World,
    *,
    layer: MapLayer,
    cursor_x: int,
    cursor_y: int,
    select_x: int | None,
    select_y: int | None,
) -> FrameInputResult:
    build = sim.build
    result = FrameInputResult(layer=layer, select_x=select_x, select_y=select_y)

    if sim.game_over:
        if inp.was_pressed(frame, "A"):
            result.reset_session = True
        return result

    if sim.research.open:
        if inp.was_pressed(frame, "B") or inp.was_pressed(frame, "SELECT"):
            sim.research.open = False
        elif inp.was_pressed(frame, "DPAD_UP") or inp.was_pressed(frame, LJOY_UP):
            sim.research.select(-1)
        elif inp.was_pressed(frame, "DPAD_DOWN") or inp.was_pressed(frame, LJOY_DOWN):
            sim.research.select(1)
        elif inp.was_pressed(frame, "A"):
            sim.start_research(world)
        return result

    if inp.was_pressed(frame, "SELECT") and build.mode == BuildMode.NONE and not sim.user_paused:
        sim.research.open = True
        return result

    if inp.was_pressed(frame, "START"):
        sim.user_paused = not sim.user_paused
    elif inp.was_pressed(frame, "Y"):
        if not sim.user_paused:
            if build.mode == BuildMode.NONE:
                build.enter_menu()
            elif build.mode == BuildMode.PLACE:
                build.back_to_menu()
    elif inp.was_pressed(frame, "B"):
        if build.mode in (BuildMode.MENU, BuildMode.PLACE):
            build.cancel_build()

    if build.mode == BuildMode.MENU:
        if inp.was_pressed(frame, "DPAD_UP") or inp.was_pressed(frame, LJOY_UP):
            build.menu_up()
        if inp.was_pressed(frame, "DPAD_DOWN") or inp.was_pressed(frame, LJOY_DOWN):
            build.menu_down()
        if inp.was_pressed(frame, "A") and not build.selected_locked(sim.research.unlocked):
            build.enter_place()

    elif build.mode == BuildMode.PLACE:
        if inp.was_pressed(frame, "A"):
            if build.try_place(world, sim.stock, cursor_x, cursor_y, sim.research.unlocked):
                if build.selected != BuildKind.CABLE:
                    build.cancel_build()

    elif not sim.user_paused:
        if inp.was_pressed(frame, "R1") and select_x is not None and select_y is not None:
            mod = world.module_at(select_x, select_y)
            if (
                mod is not None
                and mod.kind != ModuleKind.HABITAT
                and mod.state in (ModuleState.ONLINE, ModuleState.OFFLINE)
            ):
                mod.enabled = not mod.enabled
                connected = (mod.x, mod.y) in get_connected(world)
                set_module_clear(world, mod, module_active(mod, connected))
        if inp.was_pressed(frame, "X"):
            result.layer = (
                MapLayer.RESOURCES if layer == MapLayer.TERRAIN else MapLayer.TERRAIN
            )
        if inp.was_pressed(frame, "A"):
            result.select_x, result.select_y = cursor_x, cursor_y

    return result
