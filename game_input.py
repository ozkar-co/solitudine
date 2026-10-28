"""Acciones del jugador por frame — extraído de game.py."""

from __future__ import annotations

from dataclasses import dataclass

from construction import BuildController, BuildKind, BuildMode
from gamepad import LJOY_DOWN, LJOY_LEFT, LJOY_RIGHT, LJOY_UP
from input_state import FrameInput, Input
from simulation import Simulation
from ui import MapLayer
from world import World


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

    if inp.was_pressed(frame, "START"):
        sim.user_paused = not sim.user_paused
    elif inp.was_pressed(frame, "Y"):
        if build.mode == BuildMode.NONE and not sim.user_paused:
            build.enter_menu()
    elif inp.was_pressed(frame, "B"):
        if build.mode in (BuildMode.MENU, BuildMode.PLACE):
            build.cancel_build()

    if build.mode == BuildMode.MENU:
        if inp.was_pressed(frame, "DPAD_UP") or inp.was_pressed(frame, LJOY_UP):
            build.menu_up()
        if inp.was_pressed(frame, "DPAD_DOWN") or inp.was_pressed(frame, LJOY_DOWN):
            build.menu_down()
        if inp.was_pressed(frame, "A"):
            build.enter_place()

    elif build.mode == BuildMode.PLACE:
        if inp.was_pressed(frame, "A"):
            if build.try_place(world, sim.stock, cursor_x, cursor_y):
                if build.selected != BuildKind.CABLE:
                    build.cancel_build()

    elif not sim.user_paused:
        if inp.was_pressed(frame, "X"):
            result.layer = (
                MapLayer.RESOURCES if layer == MapLayer.TERRAIN else MapLayer.TERRAIN
            )
        if inp.was_pressed(frame, "A"):
            result.select_x, result.select_y = cursor_x, cursor_y

    return result
