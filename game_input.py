"""Acciones del jugador por frame — extraído de game.py."""

from __future__ import annotations

from dataclasses import dataclass

import demolition
from construction import BuildController, BuildKind, BuildMode, kind_cost
from credits import CREDITS_SCROLL_STEP, KONAMI_SEQUENCE, max_credits_scroll
from gamepad import LJOY_DOWN, LJOY_LEFT, LJOY_RIGHT, LJOY_UP
from input_state import FrameInput, Input
from logistics import network_caps
from module_defs import module_active, module_def
from network import get_connected
from resources import ResourceId
from simulation import Simulation
from ui import MapLayer
from vision import set_module_clear
from world import ModuleState, World


PAUSE_CREDITS = 1
PAUSE_OPTION_COUNT = 2


@dataclass
class FrameInputResult:
    layer: MapLayer
    select_x: int | None
    select_y: int | None
    reset_session: bool = False
    save_requested: bool = False


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

    if sim.easter_egg_open:
        if frame.pressed:
            sim.easter_egg_open = False
        return result

    if sim.game_over:
        if inp.was_pressed(frame, "A"):
            result.reset_session = True
        return result

    if sim.demolish is not None:
        if inp.was_pressed(frame, "A"):
            dx, dy = sim.demolish
            if demolition.demolish(world, sim, dx, dy):
                result.select_x = None
                result.select_y = None
                result.save_requested = True
            sim.demolish = None
        elif inp.was_pressed(frame, "B") or inp.was_pressed(frame, "START"):
            sim.demolish = None
        return result

    if sim.research.open:
        if inp.was_pressed(frame, "B"):
            sim.research.open = False
        elif inp.was_pressed(frame, "DPAD_UP") or inp.was_pressed(frame, LJOY_UP):
            sim.research.select(-1)
        elif inp.was_pressed(frame, "DPAD_DOWN") or inp.was_pressed(frame, LJOY_DOWN):
            sim.research.select(1)
        elif inp.was_pressed(frame, "A"):
            sim.start_research(world)
        return result

    if sim.user_paused:
        if sim.credits_open:
            if (
                inp.was_pressed(frame, "A")
                or inp.was_pressed(frame, "B")
                or inp.was_pressed(frame, "START")
            ):
                sim.credits_open = False
                sim.credits_scroll = 0
                sim.credits_konami = ""
            else:
                action = None
                if inp.was_pressed(frame, "DPAD_UP") or inp.was_pressed(frame, LJOY_UP):
                    action = "UP"
                elif inp.was_pressed(frame, "DPAD_DOWN") or inp.was_pressed(frame, LJOY_DOWN):
                    action = "DOWN"
                elif inp.was_pressed(frame, "DPAD_LEFT") or inp.was_pressed(frame, LJOY_LEFT):
                    action = "LEFT"
                elif inp.was_pressed(frame, "DPAD_RIGHT") or inp.was_pressed(frame, LJOY_RIGHT):
                    action = "RIGHT"
                if action is not None:
                    if action == "UP":
                        sim.credits_scroll = max(0, sim.credits_scroll - CREDITS_SCROLL_STEP)
                    elif action == "DOWN":
                        sim.credits_scroll = min(max_credits_scroll(), sim.credits_scroll + CREDITS_SCROLL_STEP)
                    sim.credits_konami = (sim.credits_konami + action[0])[-len(KONAMI_SEQUENCE):]
                    if sim.credits_konami == KONAMI_SEQUENCE:
                        sim.easter_egg_open = True
            return result
        if inp.was_pressed(frame, "START") or inp.was_pressed(frame, "B"):
            sim.user_paused = False
            sim.pause_index = 0
            sim.credits_open = False
            sim.credits_scroll = 0
            sim.credits_konami = ""
            sim.easter_egg_open = False
            return result
        if inp.was_pressed(frame, "DPAD_UP") or inp.was_pressed(frame, LJOY_UP):
            sim.pause_index = (sim.pause_index - 1) % PAUSE_OPTION_COUNT
        elif inp.was_pressed(frame, "DPAD_DOWN") or inp.was_pressed(frame, LJOY_DOWN):
            sim.pause_index = (sim.pause_index + 1) % PAUSE_OPTION_COUNT
        elif inp.was_pressed(frame, "A"):
            if sim.pause_index == PAUSE_CREDITS:
                sim.credits_open = True
                sim.credits_scroll = 0
                sim.credits_konami = ""
            else:
                sim.user_paused = False
                sim.pause_index = 0
        return result

    if inp.was_pressed(frame, "START"):
        sim.user_paused = True
        sim.pause_index = 0
        sim.credits_open = False
        sim.credits_scroll = 0
        sim.credits_konami = ""
        sim.easter_egg_open = False
        return result

    if inp.was_pressed(frame, "Y"):
        if build.mode == BuildMode.NONE:
            build.enter_menu()
        elif build.mode == BuildMode.PLACE:
            build.back_to_menu()
    elif inp.was_pressed(frame, "B"):
        if build.mode in (BuildMode.MENU, BuildMode.PLACE):
            build.cancel_build()
        elif (
            select_x is not None
            and select_y is not None
            and demolition.can_demolish(world, select_x, select_y)
        ):
            sim.demolish = (select_x, select_y)
            return result

    if build.mode == BuildMode.MENU:
        if inp.was_pressed(frame, "DPAD_UP") or inp.was_pressed(frame, LJOY_UP):
            build.menu_up()
        if inp.was_pressed(frame, "DPAD_DOWN") or inp.was_pressed(frame, LJOY_DOWN):
            build.menu_down()
        if inp.was_pressed(frame, "DPAD_LEFT") or inp.was_pressed(frame, LJOY_LEFT):
            build.menu_left()
        if inp.was_pressed(frame, "DPAD_RIGHT") or inp.was_pressed(frame, LJOY_RIGHT):
            build.menu_right()
        if (
            inp.was_pressed(frame, "A")
            and not build.selected_locked(sim.research.unlocked)
            and kind_cost(build.selected).can_afford(sim.resources)
        ):
            build.enter_place()

    elif build.mode == BuildMode.PLACE:
        if inp.was_pressed(frame, "X"):
            result.layer = (
                MapLayer.RESOURCES if layer == MapLayer.TERRAIN else MapLayer.TERRAIN
            )
        if inp.was_pressed(frame, "A"):
            if build.try_place(world, sim.resources, cursor_x, cursor_y, sim.research.unlocked):
                if build.selected != BuildKind.CABLE:
                    build.cancel_build()

    elif not sim.user_paused:
        if inp.was_pressed(frame, "R1") and select_x is not None and select_y is not None:
            mod = world.module_at(select_x, select_y)
            if (
                mod is not None
                and module_def(mod.kind).can_toggle
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
            if layer == MapLayer.RESOURCES:
                result.select_x, result.select_y = cursor_x, cursor_y
                result.layer = MapLayer.TERRAIN
            elif world.has_ruin(cursor_x, cursor_y):
                caps = network_caps(world, get_connected(world))
                space = max(0.0, caps[ResourceId.SCRAP] - sim.resources.scrap)
                taken = world.take_ruin(cursor_x, cursor_y, space)
                if taken > 0.0:
                    sim.resources.add(ResourceId.SCRAP, taken)
                    sim.stats.scrap_collected += taken
                    result.save_requested = True
                result.select_x, result.select_y = cursor_x, cursor_y
            else:
                mod = world.module_at(cursor_x, cursor_y)
                already_selected = select_x == cursor_x and select_y == cursor_y
                action = module_def(mod.kind).special_action if mod is not None else None
                connected = (
                    (mod.x, mod.y) in get_connected(world) if mod is not None else False
                )
                if (
                    already_selected
                    and mod is not None
                    and action is not None
                    and module_active(mod, connected)
                ):
                    if action == "research":
                        sim.research.open = True
                        sim.paused = True
                else:
                    result.select_x, result.select_y = cursor_x, cursor_y

    return result
