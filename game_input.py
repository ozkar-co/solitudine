"""Acciones del jugador por frame — extraído de game.py."""

from __future__ import annotations

import random
from dataclasses import dataclass

import demolition
from config import FOREST_WOOD_MAX, FOREST_WOOD_MIN
from construction import BuildController, BuildKind, BuildMode, kind_cost
from credits import CREDITS_SCROLL_STEP, KONAMI_SEQUENCE, max_credits_scroll
from gamepad import LJOY_DOWN, LJOY_LEFT, LJOY_RIGHT, LJOY_UP
from input_state import FrameInput, Input
from logistics import network_caps
from module_defs import module_active
from module_menu import ModuleMenu
from network import get_connected
from resources import ResourceId
from simulation import Simulation
from ui import MapLayer
from ui_network import max_network_scroll
from vision import set_module_clear
from world import Tile, World


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

    if sim.network_open:
        result.select_x, result.select_y = select_x, select_y
        if (
            inp.was_pressed(frame, "A")
            or inp.was_pressed(frame, "B")
            or inp.was_pressed(frame, "START")
        ):
            sim.network_open = False
            sim.network_scroll = 0
        elif inp.was_pressed(frame, "DPAD_UP") or inp.was_pressed(frame, LJOY_UP):
            sim.network_scroll = max(0, sim.network_scroll - CREDITS_SCROLL_STEP)
        elif inp.was_pressed(frame, "DPAD_DOWN") or inp.was_pressed(frame, LJOY_DOWN):
            sim.network_scroll = min(
                max_network_scroll(world, sim),
                sim.network_scroll + CREDITS_SCROLL_STEP,
            )
        return result

    if sim.module_menu is not None:
        menu = sim.module_menu
        result.select_x, result.select_y = menu.x, menu.y
        mod = world.module_at(menu.x, menu.y)
        if mod is None:
            sim.module_menu = None
            return result

        if menu.page == "fuel":
            if inp.was_pressed(frame, "B") or inp.was_pressed(frame, "START"):
                menu.page = "actions"
            elif inp.was_pressed(frame, "DPAD_UP") or inp.was_pressed(frame, LJOY_UP):
                menu.fuel_move(-1)
            elif inp.was_pressed(frame, "DPAD_DOWN") or inp.was_pressed(frame, LJOY_DOWN):
                menu.fuel_move(1)
            elif inp.was_pressed(frame, "A"):
                mod.fuel_resource = menu.current_fuel()
                if sim.resources.amount(mod.fuel_resource) <= 0.0:
                    mod.enabled = False
                result.save_requested = True
                sim.module_menu = ModuleMenu.open(world, mod, sim.resources)
            return result

        if inp.was_pressed(frame, "B") or inp.was_pressed(frame, "START"):
            sim.module_menu = None
        elif inp.was_pressed(frame, "DPAD_UP") or inp.was_pressed(frame, LJOY_UP):
            menu.move(-1)
        elif inp.was_pressed(frame, "DPAD_DOWN") or inp.was_pressed(frame, LJOY_DOWN):
            menu.move(1)
        elif inp.was_pressed(frame, "A"):
            item = menu.current()
            if item.enabled:
                if item.action == "toggle":
                    mod.enabled = not mod.enabled
                    connected = (mod.x, mod.y) in get_connected(world)
                    set_module_clear(world, mod, module_active(mod, connected))
                    result.save_requested = True
                    sim.module_menu = None
                elif item.action == "demolish":
                    sim.demolish = (menu.x, menu.y)
                    sim.module_menu = None
                elif item.action == "research":
                    sim.research.open = True
                    sim.module_menu = None
                elif item.action == "network":
                    sim.network_open = True
                    sim.network_scroll = 0
                    sim.module_menu = None
                elif item.action == "fuel":
                    menu.open_fuel(mod.fuel_resource)
                elif item.action == "close":
                    sim.module_menu = None
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
            and world.module_at(select_x, select_y) is None
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
        if inp.was_pressed(frame, "X"):
            result.layer = (
                MapLayer.RESOURCES if layer == MapLayer.TERRAIN else MapLayer.TERRAIN
            )
        if inp.was_pressed(frame, "A"):
            tile = Tile(world.tiles[world.idx(cursor_x, cursor_y)])
            already_selected = select_x == cursor_x and select_y == cursor_y
            mod = world.module_at(cursor_x, cursor_y)
            if layer == MapLayer.RESOURCES:
                result.select_x, result.select_y = cursor_x, cursor_y
                result.layer = MapLayer.TERRAIN
            elif mod is not None:
                if already_selected:
                    sim.module_menu = ModuleMenu.open(world, mod, sim.resources)
                    result.select_x, result.select_y = mod.x, mod.y
                else:
                    result.select_x, result.select_y = cursor_x, cursor_y
            elif world.has_ruin(cursor_x, cursor_y):
                if already_selected:
                    caps = network_caps(world, get_connected(world))
                    space = max(0.0, caps[ResourceId.SCRAP] - sim.resources.scrap)
                    taken = world.take_ruin(cursor_x, cursor_y, space)
                    if taken > 0.0:
                        sim.resources.add(ResourceId.SCRAP, taken)
                        sim.stats.scrap_collected += taken
                        result.save_requested = True
                result.select_x, result.select_y = cursor_x, cursor_y
            elif tile == Tile.FOREST:
                caps = network_caps(world, get_connected(world))
                amount = random.uniform(FOREST_WOOD_MIN, FOREST_WOOD_MAX)
                space = max(0.0, caps[ResourceId.WOOD] - sim.resources.wood)
                sim.resources.wood += min(space, amount)
                world.tiles[world.idx(cursor_x, cursor_y)] = Tile.SPROUT
                result.save_requested = True
                result.select_x, result.select_y = cursor_x, cursor_y
            elif tile == Tile.SPROUT:
                world.tiles[world.idx(cursor_x, cursor_y)] = Tile.GROUND
                result.save_requested = True
                result.select_x, result.select_y = cursor_x, cursor_y
            else:
                result.select_x, result.select_y = cursor_x, cursor_y

    return result
