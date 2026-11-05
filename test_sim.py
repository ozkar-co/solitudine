"""Tests mínimos de regresión: apagado y consumo de lámpara."""

from __future__ import annotations

import json
import math
import random
import tempfile
import unittest
from array import array
from pathlib import Path
from unittest.mock import patch

import demolition
import game
from config import (
    BIODIESEL_FOOD_DAILY,
    BIODIESEL_FUEL_DAILY,
    BIODIESEL_WATER_DAILY,
    COST_FISH_TRAP,
    FISH_TRAP_MAX_PER_HOUR,
    FISH_TRAP_ZERO_CHANCE,
    GREENHOUSE_FOOD_DAILY,
    GREENHOUSE_O2_DAILY,
    HABITAT_FOOD_DAILY,
    HABITAT_O2_DAILY,
    HABITAT_WATER_DAILY,
    HABITAT_X,
    HABITAT_Y,
    SECONDS_PER_DAY,
)
from construction import BuildController, BuildKind, BuildMode, BuildPreview, kind_locked
from credits import CREDITS_SCROLL_STEP
from game_input import handle_frame_input
from input_state import FrameInput, Input
from logistics import network_caps
from module_defs import buffer_cap, module_active
from module_kind import ModuleKind
from module_power import module_energy_daily
from network import get_connected, invalidate_network_cache
from network_report import build_network_report
from research import ResearchState
from resources import AlertLevel, Cost, ResourceId, ResourcePool
from savegame import delete_save, load_game, save_game
from simulation import Simulation
from tech_defs import tech_def
from vision import on_module_built
from ui import MapLayer
from ui_map import coast_overlay_plan
from ui_night import light_sources
from world import Deposit, Module, ModuleState, Tile, generate_world


def add_module(world, kind: ModuleKind, dx: int, *, enabled: bool = True) -> Module:
    mod = Module(
        kind,
        HABITAT_X + dx,
        HABITAT_Y,
        state=ModuleState.ONLINE,
        enabled=enabled,
        buffer_cap=buffer_cap(kind),
    )
    world.modules.append(mod)
    world.module_cells[(mod.x, mod.y)] = mod
    on_module_built(world, mod)
    invalidate_network_cache(world)
    return mod


def prepare_tile(world, x: int, y: int) -> None:
    i = world.idx(x, y)
    world.tiles[i] = Tile.GROUND
    world.deposits[i] = Deposit.NONE
    world.deposit_amounts[i] = 0.0
    world.explored[i] = 1
    world.visible[i] = 1
    world.ruins.pop((x, y), None)


def prepare_water(world, x: int, y: int) -> None:
    prepare_tile(world, x, y)
    i = world.idx(x, y)
    world.tiles[i] = Tile.WATER


def add_module_at(world, kind: ModuleKind, x: int, y: int, *, enabled: bool = True) -> Module:
    mod = Module(
        kind,
        x,
        y,
        state=ModuleState.ONLINE,
        enabled=enabled,
        buffer_cap=buffer_cap(kind),
    )
    world.modules.append(mod)
    world.module_cells[(x, y)] = mod
    on_module_built(world, mod)
    world._network_cache = {(x, y)}
    return mod


def run(sim: Simulation, world, seconds: float) -> None:
    for _ in range(int(seconds * 60)):
        sim.update(1 / 60, world)


class ResourceRateTests(unittest.TestCase):
    def test_days_left_uses_net_rate(self) -> None:
        pool = ResourcePool.initial()
        pool.water = 60.0
        pool.water_daily = -2.0
        self.assertAlmostEqual(pool.days_left(ResourceId.WATER), 30.0)
        self.assertEqual(pool.alert_level(ResourceId.WATER), AlertLevel.OK)

        pool.water_daily = 2.0
        self.assertEqual(pool.days_left(ResourceId.WATER), float("inf"))
        self.assertEqual(pool.alert_level(ResourceId.WATER), AlertLevel.OK)

        pool.water = 1.0
        pool.water_daily = -2.0
        self.assertEqual(pool.alert_level(ResourceId.WATER), AlertLevel.CRITICAL)


class DepletedExtractorTests(unittest.TestCase):
    def test_depleted_extractor_consumes_half_power(self) -> None:
        world = generate_world()
        sim = Simulation()
        sim.day_progress = 0.5
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                i = world.idx(HABITAT_X + 1 + dx, HABITAT_Y + dy)
                world.deposit_amounts[i] = 0.0
                world.deposits[i] = Deposit.NONE
                if Tile(world.tiles[i]) == Tile.WATER:
                    world.tiles[i] = Tile.GROUND
        add_module(world, ModuleKind.EXTRACTOR, 1)

        before = sim.resources.power
        run(sim, world, 1.0)
        self.assertAlmostEqual(before - sim.resources.power, 9.0 / 48.0, places=4)

    def test_depleted_mine_consumes_half_power(self) -> None:
        world = generate_world()
        sim = Simulation()
        sim.day_progress = 0.5
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                i = world.idx(HABITAT_X + 1 + dx, HABITAT_Y + dy)
                world.deposit_amounts[i] = 0.0
                world.deposits[i] = Deposit.NONE
        add_module(world, ModuleKind.MINE, 1)
        before = sim.resources.power
        run(sim, world, 1.0)
        self.assertAlmostEqual(before - sim.resources.power, 9.5 / 48.0, places=4)


class EnabledTests(unittest.TestCase):
    def test_disabled_fabricator_stops(self) -> None:
        world = generate_world()
        sim = Simulation()
        sim.day_progress = 0.5
        sim.resources.mineral = 100.0
        fab = add_module(world, ModuleKind.FABRICATOR, 1)
        before = sim.resources.components

        run(sim, world, 2.0)
        self.assertGreater(sim.resources.components, before)

        fab.enabled = False
        before = sim.resources.components
        run(sim, world, 2.0)
        self.assertEqual(sim.resources.components, before)

    def test_storage_cannot_be_disabled(self) -> None:
        world = generate_world()
        storage = add_module(world, ModuleKind.STORAGE, 1)
        active_cap = network_caps(world)[ResourceId.COMPONENTS]
        storage.enabled = False
        self.assertTrue(module_active(storage, True))
        self.assertEqual(network_caps(world)[ResourceId.COMPONENTS], active_cap)

    def test_habitat_stays_active(self) -> None:
        world = generate_world()
        habitat = world.module_at(HABITAT_X, HABITAT_Y)
        habitat.enabled = False
        self.assertTrue(module_active(habitat, True))


class CableNetworkTests(unittest.TestCase):
    def test_module_accepts_cables_on_all_four_sides(self) -> None:
        world = generate_world()
        stock = ResourcePool(components=10.0)
        build = BuildController()
        sides = (
            (HABITAT_X, HABITAT_Y - 1),
            (HABITAT_X + 1, HABITAT_Y),
            (HABITAT_X, HABITAT_Y + 1),
            (HABITAT_X - 1, HABITAT_Y),
        )
        for x, y in sides:
            i = world.idx(x, y)
            world.tiles[i] = Tile.GROUND
            world.explored[i] = 1

        for x, y in sides:
            self.assertTrue(build.try_place(world, stock, x, y), (x, y))
            self.assertIn((x, y), get_connected(world))


class BuildInputTests(unittest.TestCase):
    def test_y_opens_menu_from_place_mode(self) -> None:
        world = generate_world()
        sim = Simulation()
        sim.build.enter_menu()
        sim.build.menu_down()
        selected = sim.build.selected
        sim.build.enter_place()

        frame = FrameInput(frozenset({"Y"}), frozenset({"Y"}), frozenset())
        handle_frame_input(
            frame,
            Input(dev_mode=False),
            sim,
            world,
            layer=MapLayer.TERRAIN,
            cursor_x=HABITAT_X,
            cursor_y=HABITAT_Y,
            select_x=None,
            select_y=None,
        )

        self.assertEqual(sim.build.mode, BuildMode.MENU)
        self.assertEqual(sim.build.selected, selected)

    def test_build_menu_categories(self) -> None:
        build = BuildController()
        build.enter_menu()
        self.assertEqual(build.selected, BuildKind.SOLAR)

        build.menu_right()
        self.assertEqual(build.menu_category, 1)
        self.assertEqual(build.selected, BuildKind.EXTRACTOR)

        build.menu_down()
        self.assertEqual(build.selected, BuildKind.MINE)

        build.menu_right()
        self.assertEqual(build.menu_category, 2)
        self.assertEqual(build.selected, BuildKind.GREENHOUSE)

        build.menu_left()
        self.assertEqual(build.menu_category, 1)
        self.assertEqual(build.selected, BuildKind.EXTRACTOR)

    def test_unaffordable_build_item_does_not_enter_place(self) -> None:
        world = generate_world()
        sim = Simulation()
        sim.resources.components = 0.0
        sim.build.enter_menu()

        frame = FrameInput(frozenset({"A"}), frozenset({"A"}), frozenset())
        handle_frame_input(
            frame,
            Input(dev_mode=False),
            sim,
            world,
            layer=MapLayer.TERRAIN,
            cursor_x=HABITAT_X,
            cursor_y=HABITAT_Y,
            select_x=None,
            select_y=None,
        )
        self.assertEqual(sim.build.mode, BuildMode.MENU)

    def test_x_toggles_layer_in_place_mode(self) -> None:
        world = generate_world()
        sim = Simulation()
        sim.build.enter_menu()
        sim.build.enter_place()

        frame = FrameInput(frozenset({"X"}), frozenset({"X"}), frozenset())
        result = handle_frame_input(
            frame,
            Input(dev_mode=False),
            sim,
            world,
            layer=MapLayer.TERRAIN,
            cursor_x=HABITAT_X,
            cursor_y=HABITAT_Y,
            select_x=None,
            select_y=None,
        )
        self.assertEqual(result.layer, MapLayer.RESOURCES)

    def test_a_in_resource_mode_returns_to_terrain_and_selects(self) -> None:
        world = generate_world()
        sim = Simulation()

        frame = FrameInput(frozenset({"A"}), frozenset({"A"}), frozenset())
        result = handle_frame_input(
            frame,
            Input(dev_mode=False),
            sim,
            world,
            layer=MapLayer.RESOURCES,
            cursor_x=HABITAT_X,
            cursor_y=HABITAT_Y,
            select_x=None,
            select_y=None,
        )
        self.assertEqual(result.layer, MapLayer.TERRAIN)
        self.assertEqual((result.select_x, result.select_y), (HABITAT_X, HABITAT_Y))

    def test_a_again_on_selected_lab_opens_research(self) -> None:
        world = generate_world()
        sim = Simulation()
        lab = add_module(world, ModuleKind.LABORATORY, 1)
        frame = FrameInput(frozenset({"A"}), frozenset({"A"}), frozenset())

        first = handle_frame_input(
            frame,
            Input(dev_mode=False),
            sim,
            world,
            layer=MapLayer.TERRAIN,
            cursor_x=lab.x,
            cursor_y=lab.y,
            select_x=None,
            select_y=None,
        )
        self.assertEqual((first.select_x, first.select_y), (lab.x, lab.y))
        self.assertFalse(sim.research.open)

        second = handle_frame_input(
            frame,
            Input(dev_mode=False),
            sim,
            world,
            layer=MapLayer.TERRAIN,
            cursor_x=lab.x,
            cursor_y=lab.y,
            select_x=first.select_x,
            select_y=first.select_y,
        )
        self.assertIsNotNone(sim.module_menu)
        self.assertFalse(sim.research.open)

        handle_frame_input(
            frame,
            Input(dev_mode=False),
            sim,
            world,
            layer=MapLayer.TERRAIN,
            cursor_x=lab.x,
            cursor_y=lab.y,
            select_x=second.select_x,
            select_y=second.select_y,
        )
        self.assertTrue(sim.research.open)

    def test_r1_does_not_toggle_storage(self) -> None:
        world = generate_world()
        sim = Simulation()
        storage = add_module(world, ModuleKind.STORAGE, 1)
        frame = FrameInput(frozenset({"R1"}), frozenset({"R1"}), frozenset())

        handle_frame_input(
            frame,
            Input(dev_mode=False),
            sim,
            world,
            layer=MapLayer.TERRAIN,
            cursor_x=storage.x,
            cursor_y=storage.y,
            select_x=storage.x,
            select_y=storage.y,
        )
        self.assertTrue(storage.enabled)

    def test_a_again_on_building_lab_does_not_open_research(self) -> None:
        world = generate_world()
        sim = Simulation()
        lab = add_module(world, ModuleKind.LABORATORY, 1)
        lab.state = ModuleState.BUILDING
        frame = FrameInput(frozenset({"A"}), frozenset({"A"}), frozenset())

        first = handle_frame_input(
            frame,
            Input(dev_mode=False),
            sim,
            world,
            layer=MapLayer.TERRAIN,
            cursor_x=lab.x,
            cursor_y=lab.y,
            select_x=None,
            select_y=None,
        )
        self.assertEqual((first.select_x, first.select_y), (lab.x, lab.y))

        handle_frame_input(
            frame,
            Input(dev_mode=False),
            sim,
            world,
            layer=MapLayer.TERRAIN,
            cursor_x=lab.x,
            cursor_y=lab.y,
            select_x=first.select_x,
            select_y=first.select_y,
        )
        self.assertFalse(sim.research.open)

    def test_select_is_free(self) -> None:
        world = generate_world()
        sim = Simulation()
        frame = FrameInput(frozenset({"SELECT"}), frozenset({"SELECT"}), frozenset())

        result = handle_frame_input(
            frame,
            Input(dev_mode=False),
            sim,
            world,
            layer=MapLayer.TERRAIN,
            cursor_x=HABITAT_X,
            cursor_y=HABITAT_Y,
            select_x=None,
            select_y=None,
        )
        self.assertFalse(sim.research.open)
        self.assertFalse(sim.user_paused)
        self.assertIsNone(result.select_x)

        sim.research.open = True
        handle_frame_input(
            frame,
            Input(dev_mode=False),
            sim,
            world,
            layer=MapLayer.TERRAIN,
            cursor_x=HABITAT_X,
            cursor_y=HABITAT_Y,
            select_x=None,
            select_y=None,
        )
        self.assertTrue(sim.research.open)


class StartupTests(unittest.TestCase):
    def test_wait_for_start_requires_start(self) -> None:
        class FakeInput:
            def __init__(self) -> None:
                self.polls = 0
                self.events = []

            def process_event(self, event) -> None:
                self.events.append(event)

            def poll(self) -> FrameInput:
                self.polls += 1
                if self.polls < 3:
                    return FrameInput(frozenset(), frozenset(), frozenset())
                return FrameInput(frozenset({"START"}), frozenset({"START"}), frozenset())

        inp = FakeInput()
        with (
            patch.object(game, "draw_splash"),
            patch.object(game, "present"),
            patch.object(game.pygame.event, "get", return_value=[]),
            patch.object(game.pygame.time, "wait"),
        ):
            self.assertTrue(game.wait_for_start(None, None, inp, "SOLITUDINE"))
        self.assertEqual(inp.polls, 3)


class SaveTests(unittest.TestCase):
    def test_roundtrip(self) -> None:
        world = generate_world()
        sim = Simulation()
        sim.day = 2
        sim.day_progress = 0.42
        sim.resources.components = 31.0
        sim.resources.scrap = 12.0
        sim.resources.wood = 4.0
        sim.resources.coal = 5.0
        sim.resources.fuel = 6.0
        sim.resources.crystal = 7.0
        sim.stats.scrap_collected = 3.0
        sim.stats.scrap_processed = 2.0
        fab = add_module(world, ModuleKind.FABRICATOR, 1, enabled=False)
        fab.built_day = 3
        fab.cost_paid = Cost({"components": 5.0, "mineral": 2.0})
        lamp = add_module(world, ModuleKind.LAMP, 2)
        sim.resources.power = 33.0
        sim.research.unlocked = {"condensador"}
        sim.research.active = "electrolisis"
        sim.research.progress = 0.5

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "save.json"
            save_game(world, sim, path)
            loaded = load_game(path)
            self.assertIsNotNone(loaded)
            world2, sim2 = loaded
            self.assertEqual(sim2.day, 2)
            self.assertAlmostEqual(sim2.day_progress, 0.42)
            self.assertEqual(sim2.resources.components, 31.0)
            self.assertEqual(sim2.resources.scrap, 12.0)
            self.assertEqual(sim2.resources.wood, 4.0)
            self.assertEqual(sim2.resources.coal, 5.0)
            self.assertEqual(sim2.resources.fuel, 6.0)
            self.assertEqual(sim2.resources.crystal, 7.0)
            self.assertEqual(sim2.resources.power, 33.0)
            self.assertEqual(world2.seed, world.seed)
            self.assertEqual(world2.size, world.size)
            self.assertEqual(sim2.stats.scrap_collected, 3.0)
            self.assertEqual(sim2.stats.scrap_processed, 2.0)
            self.assertEqual(world2.ruins, world.ruins)
            mod = world2.module_at(fab.x, fab.y)
            self.assertIsNotNone(mod)
            self.assertFalse(mod.enabled)
            self.assertEqual(mod.built_day, 3)
            self.assertEqual(mod.cost_paid.amounts[ResourceId.COMPONENTS], 5.0)
            self.assertEqual(mod.cost_paid.amounts[ResourceId.MINERAL], 2.0)
            self.assertEqual(world2.module_at(lamp.x, lamp.y).kind, ModuleKind.LAMP)
            self.assertEqual(sim2.research.unlocked, {"condensador"})
            self.assertEqual(sim2.research.active, "electrolisis")
            self.assertAlmostEqual(sim2.research.progress, 0.5)
            delete_save(path)
            self.assertIsNone(load_game(path))

    def test_size_and_seed_roundtrip(self) -> None:
        world = generate_world(seed="CUSTOM", size=256)
        sim = Simulation()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "save.json"
            save_game(world, sim, path)
            loaded = load_game(path)
            self.assertIsNotNone(loaded)
            world2, _ = loaded
            self.assertEqual(world2.size, 256)
            self.assertEqual(world2.seed, "CUSTOM")
            self.assertEqual(len(world2.tiles), 256 * 256)
            delete_save(path)

    def test_death_state_roundtrip(self) -> None:
        world = generate_world()
        sim = Simulation()
        sim.resources.o2 = 0.0
        sim.update(1 / 60, world)
        self.assertTrue(sim.game_over)
        self.assertEqual(sim.death_cause, "death.o2")

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "save.json"
            save_game(world, sim, path)
            loaded = load_game(path)
            self.assertIsNotNone(loaded)
            _world, sim2 = loaded
            self.assertTrue(sim2.game_over)
            self.assertTrue(sim2.paused)
            self.assertEqual(sim2.death_cause, "death.o2")

    def test_old_version_save_is_deleted(self) -> None:
        world = generate_world()
        sim = Simulation()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "save.json"
            save_game(world, sim, path)
            data = json.loads(path.read_text(encoding="utf-8"))
            data["version"] = 3
            path.write_text(json.dumps(data), encoding="utf-8")
            self.assertIsNone(load_game(path))
            self.assertFalse(path.exists())


class ResearchTests(unittest.TestCase):
    def test_research_spends_and_completes(self) -> None:
        world = generate_world()
        sim = Simulation()
        sim.day_progress = 0.5
        lab = add_module(world, ModuleKind.LABORATORY, 1)
        before = sim.resources.components
        self.assertTrue(sim.start_research(world))
        self.assertEqual(sim.resources.components, before - 4.0)
        run(sim, world, 1.0)
        self.assertGreater(sim.research.progress, 0.0)
        lab.enabled = False
        paused_at = sim.research.progress
        run(sim, world, 1.0)
        self.assertEqual(sim.research.progress, paused_at)
        lab.enabled = True
        run(sim, world, 100.0)
        self.assertIn("electrolisis", sim.research.unlocked)
        self.assertIsNone(sim.research.active)

    def test_research_needs_lab(self) -> None:
        world = generate_world()
        sim = Simulation()
        before = sim.resources.components
        self.assertFalse(sim.start_research(world))
        self.assertEqual(sim.resources.components, before)

    def test_tech_gating(self) -> None:
        self.assertTrue(kind_locked(BuildKind.ELECTROLYZER, set()))
        self.assertFalse(kind_locked(BuildKind.ELECTROLYZER, {"electrolisis"}))
        self.assertTrue(kind_locked(BuildKind.CONDENSER, set()))


class BalanceTests(unittest.TestCase):
    def test_initial_reserve_days(self) -> None:
        sim = Simulation()
        self.assertAlmostEqual(sim.resources.days_left(ResourceId.O2), 12.0)
        self.assertAlmostEqual(sim.resources.days_left(ResourceId.WATER), 9.0)
        self.assertAlmostEqual(sim.resources.days_left(ResourceId.FOOD), 7.0)
        self.assertAlmostEqual(sim.resources.days_left(ResourceId.POWER), 10.0)


class GreenhouseTests(unittest.TestCase):
    def test_o2_production_requires_water(self) -> None:
        def o2_after(with_greenhouse: bool, water: float) -> float:
            world = generate_world()
            sim = Simulation()
            sim.day_progress = 0.5
            sim.resources.o2 = 50.0
            sim.resources.water = water
            if with_greenhouse:
                add_module(world, ModuleKind.GREENHOUSE, 1)
            run(sim, world, 1.0)
            return sim.resources.o2

        self.assertGreater(o2_after(True, 10.0), o2_after(False, 10.0))
        self.assertAlmostEqual(o2_after(True, 0.0), o2_after(False, 0.0), places=4)


class TechModuleTests(unittest.TestCase):
    def test_electrolyzer_produces_o2(self) -> None:
        def after(with_electrolyzer: bool) -> tuple[float, float]:
            world = generate_world()
            sim = Simulation()
            sim.day_progress = 0.5
            sim.resources.water = 20.0
            sim.resources.o2 = 40.0
            if with_electrolyzer:
                add_module(world, ModuleKind.ELECTROLYZER, 1)
            run(sim, world, 1.0)
            return sim.resources.water, sim.resources.o2

        water_with, o2_with = after(True)
        water_without, o2_without = after(False)
        self.assertLess(water_with, water_without)
        self.assertGreater(o2_with, o2_without)

    def test_condenser_produces_water(self) -> None:
        def water_after(seconds: float, with_condenser: bool) -> float:
            world = generate_world()
            sim = Simulation()
            sim.day_progress = 0.5
            sim.resources.water = 10.0
            if with_condenser:
                add_module(world, ModuleKind.CONDENSER, 1)
            run(sim, world, seconds)
            return sim.resources.water

        self.assertGreater(water_after(1.0, True), water_after(1.0, False))


class LampTests(unittest.TestCase):
    def test_lamp_power_only_at_night(self) -> None:
        world = generate_world()
        lamp = add_module(world, ModuleKind.LAMP, 1)

        self.assertEqual(module_energy_daily(lamp, world, hour_float=12.0), 0.0)
        self.assertAlmostEqual(module_energy_daily(lamp, world, hour_float=0.0), -4.0)
        self.assertAlmostEqual(module_energy_daily(lamp, world, hour_float=18.0), -4.0 / 3.0)

    def test_disabled_lamp_consumes_nothing(self) -> None:
        world = generate_world()
        lamp = add_module(world, ModuleKind.LAMP, 1, enabled=False)
        self.assertEqual(module_energy_daily(lamp, world, hour_float=0.0), 0.0)

    def test_disabled_lamp_does_not_light(self) -> None:
        world = generate_world()
        lamp = add_module(world, ModuleKind.LAMP, 1)
        connected = get_connected(world)
        self.assertIn((lamp.x, lamp.y, 10), light_sources(world, connected))
        lamp.enabled = False
        self.assertNotIn((lamp.x, lamp.y, 10), light_sources(world, connected))
        self.assertIn((HABITAT_X, HABITAT_Y, 8), light_sources(world, connected))


class PauseMenuTests(unittest.TestCase):
    def _press(self, sim: Simulation, world, *keys: str) -> None:
        frame = FrameInput(held=frozenset(), pressed=frozenset(keys), released=frozenset())
        handle_frame_input(
            frame,
            Input(False),
            sim,
            world,
            layer=MapLayer.TERRAIN,
            cursor_x=0,
            cursor_y=0,
            select_x=None,
            select_y=None,
        )

    def test_pause_menu_opens_credits(self) -> None:
        world = generate_world()
        sim = Simulation()

        self._press(sim, world, "START")
        self.assertTrue(sim.user_paused)

        self._press(sim, world, "DPAD_DOWN")
        self.assertEqual(sim.pause_index, 1)

        self._press(sim, world, "A")
        self.assertTrue(sim.credits_open)
        self.assertTrue(sim.user_paused)

        self._press(sim, world, "DPAD_DOWN")
        self.assertEqual(sim.credits_scroll, CREDITS_SCROLL_STEP)
        self._press(sim, world, "DPAD_UP")
        self.assertEqual(sim.credits_scroll, 0)

        self._press(sim, world, "B")
        self.assertFalse(sim.credits_open)
        self.assertTrue(sim.user_paused)

        self._press(sim, world, "START")
        self.assertFalse(sim.user_paused)
        self.assertEqual(sim.pause_index, 0)

    def test_pause_menu_continue(self) -> None:
        world = generate_world()
        sim = Simulation()

        self._press(sim, world, "START")
        self._press(sim, world, "A")
        self.assertFalse(sim.user_paused)
        self.assertEqual(sim.pause_index, 0)

    def test_credits_konami_opens_cat_photo(self) -> None:
        world = generate_world()
        sim = Simulation()

        self._press(sim, world, "START")
        self._press(sim, world, "DPAD_DOWN")
        self._press(sim, world, "A")
        self.assertTrue(sim.credits_open)

        for key in (
            "DPAD_UP",
            "DPAD_UP",
            "DPAD_DOWN",
            "DPAD_DOWN",
            "DPAD_LEFT",
            "DPAD_RIGHT",
            "DPAD_LEFT",
            "DPAD_RIGHT",
        ):
            self._press(sim, world, key)

        self.assertTrue(sim.easter_egg_open)

        self._press(sim, world, "A")
        self.assertFalse(sim.easter_egg_open)
        self.assertTrue(sim.credits_open)


class CostTests(unittest.TestCase):
    def test_multi_cost_spend_is_atomic(self) -> None:
        pool = ResourcePool(components=4.0, mineral=1.0)
        cost = Cost({"components": 5.0, "mineral": 2.0})
        self.assertFalse(cost.spend(pool))
        self.assertEqual(pool.components, 4.0)
        self.assertEqual(pool.mineral, 1.0)
        self.assertEqual(cost.missing(pool)[ResourceId.COMPONENTS], 1.0)
        self.assertEqual(cost.missing(pool)[ResourceId.MINERAL], 1.0)

    def test_refund_respects_cap(self) -> None:
        pool = ResourcePool()
        cost = Cost({"components": 5.0})
        caps = {resource: 10.0 for resource in ResourceId}
        caps[ResourceId.COMPONENTS] = 3.0
        refunded = cost.refund(pool, 1.0, caps)
        self.assertEqual(pool.components, 3.0)
        self.assertEqual(refunded.amounts[ResourceId.COMPONENTS], 3.0)


class MultiCostBuildTests(unittest.TestCase):
    def test_fabricator_spends_two_resources_and_records_paid(self) -> None:
        world = generate_world()
        sim = Simulation()
        x, y = HABITAT_X + 1, HABITAT_Y
        prepare_tile(world, x, y)
        sim.resources.components = 10.0
        sim.resources.mineral = 5.0
        sim.build.selected = BuildKind.FABRICATOR

        self.assertTrue(sim.build.try_place(world, sim.resources, x, y, set()))
        self.assertEqual(sim.resources.components, 5.0)
        self.assertEqual(sim.resources.mineral, 3.0)
        mod = world.module_at(x, y)
        self.assertIsNotNone(mod)
        self.assertEqual(mod.cost_paid.amounts[ResourceId.COMPONENTS], 5.0)
        self.assertEqual(mod.cost_paid.amounts[ResourceId.MINERAL], 2.0)


class ScrapTests(unittest.TestCase):
    def test_world_has_ruins_in_open_ground(self) -> None:
        world = generate_world()
        self.assertEqual(len(world.ruins), 26)
        for (x, y), amount in world.ruins.items():
            i = world.idx(x, y)
            self.assertGreater(amount, 0.0)
            self.assertEqual(Tile(world.tiles[i]), Tile.GROUND)
            self.assertEqual(Deposit(world.deposits[i]), Deposit.NONE)
            self.assertNotEqual((x, y), (HABITAT_X, HABITAT_Y))

    def test_ruin_blocks_building_and_cables(self) -> None:
        world = generate_world()
        sim = Simulation()
        x, y = next(iter(world.ruins))
        world.explored[world.idx(x, y)] = 1
        sim.build.selected = BuildKind.SOLAR
        self.assertEqual(sim.build.preview(world, sim.resources, x, y), BuildPreview.RUIN)
        sim.build.selected = BuildKind.CABLE
        self.assertEqual(sim.build.preview(world, sim.resources, x, y), BuildPreview.RUIN)

    def test_collect_ruin_with_a(self) -> None:
        world = generate_world()
        sim = Simulation()
        x, y = next(iter(world.ruins))
        amount = world.ruin_amount(x, y)
        world.explored[world.idx(x, y)] = 1
        frame = FrameInput(frozenset({"A"}), frozenset({"A"}), frozenset())

        first = handle_frame_input(
            frame,
            Input(dev_mode=False),
            sim,
            world,
            layer=MapLayer.TERRAIN,
            cursor_x=x,
            cursor_y=y,
            select_x=None,
            select_y=None,
        )
        self.assertEqual(sim.resources.scrap, 0.0)
        self.assertTrue(world.has_ruin(x, y))
        self.assertFalse(first.save_requested)

        second = handle_frame_input(
            frame,
            Input(dev_mode=False),
            sim,
            world,
            layer=MapLayer.TERRAIN,
            cursor_x=x,
            cursor_y=y,
            select_x=first.select_x,
            select_y=first.select_y,
        )
        self.assertAlmostEqual(sim.resources.scrap, min(amount, 30.0))
        self.assertFalse(world.has_ruin(x, y))
        self.assertAlmostEqual(sim.stats.scrap_collected, min(amount, 30.0))
        self.assertTrue(second.save_requested)

    def test_collect_respects_scrap_cap(self) -> None:
        world = generate_world()
        sim = Simulation()
        x, y = next(iter(world.ruins))
        amount = world.ruin_amount(x, y)
        sim.resources.scrap = 29.0
        frame = FrameInput(frozenset({"A"}), frozenset({"A"}), frozenset())
        first = handle_frame_input(
            frame,
            Input(dev_mode=False),
            sim,
            world,
            layer=MapLayer.TERRAIN,
            cursor_x=x,
            cursor_y=y,
            select_x=None,
            select_y=None,
        )
        handle_frame_input(
            frame,
            Input(dev_mode=False),
            sim,
            world,
            layer=MapLayer.TERRAIN,
            cursor_x=x,
            cursor_y=y,
            select_x=first.select_x,
            select_y=first.select_y,
        )
        self.assertAlmostEqual(sim.resources.scrap, 30.0)
        self.assertTrue(world.has_ruin(x, y))
        self.assertAlmostEqual(world.ruin_amount(x, y), amount - 1.0)


class DemolitionTests(unittest.TestCase):
    def test_demolish_module_creates_ruin(self) -> None:
        world = generate_world()
        sim = Simulation()
        x, y = HABITAT_X + 1, HABITAT_Y
        prepare_tile(world, x, y)
        mod = add_module(world, ModuleKind.FABRICATOR, 1)
        mod.cost_paid = Cost({"components": 5.0, "mineral": 2.0})
        self.assertTrue(demolition.demolish(world, sim, x, y))
        self.assertIsNone(world.module_at(x, y))
        self.assertTrue(world.has_ruin(x, y))
        mineral_value = 5.0 * 1.5 + 2.0
        scrap = world.ruin_amount(x, y)
        self.assertGreaterEqual(scrap, mineral_value * 0.6 - 1e-6)
        self.assertLessEqual(scrap, mineral_value * 0.9 + 1e-6)

    def test_cable_refunds_components(self) -> None:
        world = generate_world()
        sim = Simulation()
        x, y = HABITAT_X + 1, HABITAT_Y
        prepare_tile(world, x, y)
        world.cables.add((x, y))
        sim.resources.components = 0.0
        self.assertTrue(demolition.demolish(world, sim, x, y))
        self.assertNotIn((x, y), world.cables)
        self.assertEqual(sim.resources.components, 1.0)

    def test_cancel_site_returns_scrap_for_progress(self) -> None:
        world = generate_world()
        sim = Simulation()
        x, y = HABITAT_X + 1, HABITAT_Y
        prepare_tile(world, x, y)
        mod = add_module(world, ModuleKind.FABRICATOR, 1)
        mod.state = ModuleState.BUILDING
        mod.build_progress = 0.5
        mod.build_total = 1.0
        mod.cost_paid = Cost({"components": 10.0, "mineral": 5.0})
        self.assertTrue(demolition.demolish(world, sim, x, y))
        self.assertAlmostEqual(sim.resources.scrap, 5.0)
        self.assertFalse(world.has_ruin(x, y))

    def test_cancel_site_caps_at_ninety_percent(self) -> None:
        world = generate_world()
        sim = Simulation()
        x, y = HABITAT_X + 1, HABITAT_Y
        prepare_tile(world, x, y)
        mod = add_module(world, ModuleKind.FABRICATOR, 1)
        mod.state = ModuleState.BUILDING
        mod.build_progress = 1.0
        mod.build_total = 1.0
        mod.cost_paid = Cost({"components": 10.0})
        self.assertTrue(demolition.demolish(world, sim, x, y))
        self.assertAlmostEqual(sim.resources.scrap, 9.0)

    def test_habitat_cannot_be_demolished(self) -> None:
        world = generate_world()
        sim = Simulation()
        self.assertFalse(demolition.demolish(world, sim, HABITAT_X, HABITAT_Y))

    def test_b_opens_confirmation_and_a_demolishes(self) -> None:
        world = generate_world()
        sim = Simulation()
        x, y = HABITAT_X + 1, HABITAT_Y
        prepare_tile(world, x, y)
        mod = add_module(world, ModuleKind.FABRICATOR, 1)
        mod.cost_paid = Cost({"components": 5.0, "mineral": 2.0})
        inp = Input(dev_mode=False)

        def press(key: str, select_x, select_y):
            frame = FrameInput(frozenset({key}), frozenset({key}), frozenset())
            return handle_frame_input(
                frame,
                inp,
                sim,
                world,
                layer=MapLayer.TERRAIN,
                cursor_x=x,
                cursor_y=y,
                select_x=select_x,
                select_y=select_y,
            )

        selected = press("A", None, None)
        self.assertEqual((selected.select_x, selected.select_y), (x, y))
        opened = press("A", selected.select_x, selected.select_y)
        self.assertIsNotNone(sim.module_menu)
        press("DPAD_DOWN", opened.select_x, opened.select_y)
        press("A", opened.select_x, opened.select_y)
        self.assertEqual(sim.demolish, (x, y))

        confirmed = press("A", selected.select_x, selected.select_y)
        self.assertIsNone(sim.demolish)
        self.assertIsNone(world.module_at(x, y))
        self.assertTrue(world.has_ruin(x, y))
        self.assertTrue(confirmed.save_requested)


class RecyclerTests(unittest.TestCase):
    def test_tech_gating(self) -> None:
        self.assertTrue(kind_locked(BuildKind.RECYCLER, set()))
        self.assertFalse(kind_locked(BuildKind.RECYCLER, {"reciclaje"}))

    def test_research_spends_scrap(self) -> None:
        tech = tech_def("reciclaje")
        pool = ResourcePool(components=2.0, mineral=1.0, scrap=5.0)
        state = ResearchState()
        self.assertTrue(state.start(tech, pool, True))
        self.assertEqual(pool.scrap, 0.0)
        self.assertEqual(pool.components, 0.0)
        self.assertEqual(pool.mineral, 0.0)

    def test_recycler_converts_scrap(self) -> None:
        world = generate_world()
        sim = Simulation()
        x, y = HABITAT_X + 1, HABITAT_Y
        prepare_tile(world, x, y)
        add_module(world, ModuleKind.RECYCLER, 1)
        sim.day_progress = 0.5
        sim.resources.scrap = 10.0
        sim.resources.water = 100.0
        sim.resources.mineral = 0.0
        sim.resources.components = 0.0
        sim.resources.power = 100.0

        run(sim, world, 1.0)
        self.assertLess(sim.resources.scrap, 10.0)
        self.assertGreater(sim.resources.mineral, 0.0)
        self.assertGreater(sim.stats.scrap_processed, 0.0)

    def test_recycler_stops_without_scrap(self) -> None:
        world = generate_world()
        sim = Simulation()
        x, y = HABITAT_X + 1, HABITAT_Y
        prepare_tile(world, x, y)
        add_module(world, ModuleKind.RECYCLER, 1)
        sim.day_progress = 0.5
        sim.resources.scrap = 0.0
        sim.resources.mineral = 0.0
        sim.resources.water = 100.0
        sim.resources.power = 100.0

        run(sim, world, 1.0)
        self.assertEqual(sim.resources.mineral, 0.0)
        self.assertEqual(sim.stats.scrap_processed, 0.0)


if __name__ == "__main__":
    unittest.main()


class FishTrapTests(unittest.TestCase):
    def _trap(self, water: bool = True):
        world = generate_world()
        sim = Simulation()
        x, y = HABITAT_X + 1, HABITAT_Y
        prepare_tile(world, x, y)
        if water:
            world.tiles[world.idx(x, y)] = Tile.WATER
        mod = add_module_at(world, ModuleKind.FISH_TRAP, x, y)
        return world, sim, mod

    def test_placement_only_on_water(self) -> None:
        world = generate_world()
        sim = Simulation()
        x, y = HABITAT_X + 1, HABITAT_Y
        prepare_tile(world, x, y)
        sim.build.selected = BuildKind.FISH_TRAP
        self.assertEqual(
            sim.build.preview(world, sim.resources, x, y),
            BuildPreview.BAD_TERRAIN,
        )
        world.tiles[world.idx(x, y)] = Tile.WATER
        self.assertEqual(
            sim.build.preview(world, sim.resources, x, y),
            BuildPreview.OK,
        )

    def test_cable_can_be_placed_on_water(self) -> None:
        world = generate_world()
        sim = Simulation()
        x, y = HABITAT_X + 1, HABITAT_Y
        prepare_water(world, x, y)
        sim.build.selected = BuildKind.CABLE
        self.assertTrue(sim.build.try_place(world, sim.resources, x, y))
        self.assertIn((x, y), world.cables)

    def test_hourly_roll_only_at_night(self) -> None:
        world, sim, mod = self._trap()
        sim.day = 1
        sim.day_progress = 20.9 / 24
        sim.last_hour_index = 20
        with patch.object(sim.rng, "random", return_value=0.9), patch.object(
            sim.rng, "uniform", return_value=1.0
        ):
            sim.update((0.2 / 24) * SECONDS_PER_DAY, world)
        self.assertGreater(mod.buffer + sim.resources.food, 56.5)

    def test_daytime_and_no_water_do_not_roll(self) -> None:
        world, sim, mod = self._trap()
        sim.day = 1
        sim.day_progress = 12.9 / 24
        sim.last_hour_index = 12
        with patch.object(sim.rng, "random", return_value=0.9), patch.object(
            sim.rng, "uniform", return_value=1.0
        ):
            sim.update((0.2 / 24) * SECONDS_PER_DAY, world)
        self.assertEqual(mod.buffer, 0.0)

        world2, sim2, mod2 = self._trap(water=False)
        sim2.day = 1
        sim2.day_progress = 20.9 / 24
        sim2.last_hour_index = 20
        with patch.object(sim2.rng, "random", return_value=0.9), patch.object(
            sim2.rng, "uniform", return_value=1.0
        ):
            sim2.update((0.2 / 24) * SECONDS_PER_DAY, world2)
        self.assertEqual(mod2.buffer, 0.0)

    def test_rng_average_is_about_three_per_night(self) -> None:
        world, sim, mod = self._trap()
        sim.rng = random.Random(7)
        total = 0.0
        for _ in range(2000):
            sim.resources.food = 0.0
            mod.buffer = 0.0
            sim._roll_fish_traps(world)
            total += sim.resources.food + mod.buffer
        self.assertGreater(total / 2000.0, 0.30)
        self.assertLess(total / 2000.0, 0.45)

    def test_demolition_returns_scrap_without_ruin(self) -> None:
        world, sim, mod = self._trap()
        x, y = mod.x, mod.y
        self.assertTrue(demolition.demolish(world, sim, x, y))
        self.assertNotIn((x, y), world.ruins)
        self.assertGreater(sim.resources.scrap, 0.0)


class BiodieselTests(unittest.TestCase):
    def test_biodiesel_consumes_food_and_water_and_makes_fuel(self) -> None:
        world = generate_world()
        sim = Simulation()
        sim.day_progress = 0.5
        sim.resources.food = 50.0
        sim.resources.water = 20.0
        sim.resources.power = 100.0
        add_module(world, ModuleKind.BIODIESEL, 1)
        run(sim, world, 1.0)
        self.assertGreater(sim.resources.fuel, 0.0)
        self.assertAlmostEqual(50.0 - sim.resources.food, (HABITAT_FOOD_DAILY + BIODIESEL_FOOD_DAILY) / 48.0, places=4)
        self.assertAlmostEqual(20.0 - sim.resources.water, (HABITAT_WATER_DAILY + BIODIESEL_WATER_DAILY) / 48.0, places=4)


class GreenhouseBalanceTests(unittest.TestCase):
    def test_greenhouse_produces_six_food_and_three_o2(self) -> None:
        world = generate_world()
        sim = Simulation()
        sim.day_progress = 0.5
        sim.resources.food = 50.0
        sim.resources.o2 = 40.0
        sim.resources.water = 100.0
        sim.resources.power = 100.0
        add_module(world, ModuleKind.GREENHOUSE, 1)
        run(sim, world, 1.0)
        self.assertAlmostEqual(50.0 - sim.resources.food, (HABITAT_FOOD_DAILY - GREENHOUSE_FOOD_DAILY) / 48.0, places=4)
        self.assertAlmostEqual(sim.resources.o2 - 40.0, (GREENHOUSE_O2_DAILY - HABITAT_O2_DAILY) / 48.0, places=4)


class ForestTests(unittest.TestCase):
    def test_harvest_forest_leaves_sprout_and_gives_wood(self) -> None:
        world = generate_world()
        sim = Simulation()
        x, y = HABITAT_X + 1, HABITAT_Y
        prepare_tile(world, x, y)
        world.tiles[world.idx(x, y)] = Tile.FOREST
        frame = FrameInput(frozenset({"A"}), frozenset({"A"}), frozenset())
        result = handle_frame_input(
            frame,
            Input(dev_mode=False),
            sim,
            world,
            layer=MapLayer.TERRAIN,
            cursor_x=x,
            cursor_y=y,
            select_x=None,
            select_y=None,
        )
        self.assertGreater(sim.resources.wood, 0.0)
        self.assertEqual(Tile(world.tiles[world.idx(x, y)]), Tile.SPROUT)
        self.assertTrue(result.save_requested)

        wood = sim.resources.wood
        handle_frame_input(
            frame,
            Input(dev_mode=False),
            sim,
            world,
            layer=MapLayer.TERRAIN,
            cursor_x=x,
            cursor_y=y,
            select_x=x,
            select_y=y,
        )
        self.assertEqual(Tile(world.tiles[world.idx(x, y)]), Tile.GROUND)
        self.assertEqual(sim.resources.wood, wood)


class WorldGenerationTests(unittest.TestCase):
    def test_parameterized_size_seed_and_compact_arrays(self) -> None:
        world = generate_world(seed="TEST", size=256)
        self.assertEqual(world.size, 256)
        self.assertEqual(world.seed, "TEST")
        self.assertEqual(len(world.tiles), 256 * 256)
        self.assertIsInstance(world.tiles, bytearray)
        self.assertIsInstance(world.deposits, bytearray)
        self.assertIsInstance(world.deposit_amounts, array)

    def test_deterministic_seed(self) -> None:
        a = generate_world(seed="A", size=128)
        b = generate_world(seed="A", size=128)
        c = generate_world(seed="B", size=128)
        self.assertEqual(bytes(a.tiles), bytes(b.tiles))
        self.assertEqual(bytes(a.deposits), bytes(b.deposits))
        self.assertNotEqual(bytes(a.tiles), bytes(c.tiles))

    def test_new_content_guarantees(self) -> None:
        world = generate_world(seed="TEST", size=512)
        hx, hy = world.habitat_x, world.habitat_y
        forest_near = False
        coal_edge = False
        crystal = False
        for y in range(world.size):
            for x in range(world.size):
                i = world.idx(x, y)
                if Tile(world.tiles[i]) == Tile.FOREST and math.hypot(x - hx, y - hy) <= 20:
                    forest_near = True
                dep = Deposit(world.deposits[i])
                if dep == Deposit.COAL:
                    d = math.hypot(x - hx, y - hy)
                    if 18 <= d <= 30:
                        coal_edge = True
                if dep == Deposit.CRYSTAL:
                    crystal = True
        self.assertTrue(forest_near)
        self.assertTrue(coal_edge)
        self.assertTrue(crystal)

    def test_deposit_coverage_is_not_empty(self) -> None:
        world = generate_world(seed="TEST", size=512)
        chunk = 64
        covered = 0
        total = 0
        for cy in range(0, world.size, chunk):
            for cx in range(0, world.size, chunk):
                total += 1
                found = False
                for y in range(cy, min(world.size, cy + chunk)):
                    for x in range(cx, min(world.size, cx + chunk)):
                        dep = Deposit(world.deposits[world.idx(x, y)])
                        if dep in (Deposit.WATER, Deposit.MINERAL):
                            found = True
                            break
                    if found:
                        break
                if found:
                    covered += 1
        self.assertGreater(covered / total, 0.25)


class BuildModalTests(unittest.TestCase):
    def test_category_carousel_animates_to_target(self) -> None:
        build = BuildController()
        build.enter_menu()
        build.menu_right()
        self.assertEqual(build.menu_category, 1)
        self.assertEqual(build.category_visual_target, 1.0)
        build.update(1.0)
        self.assertAlmostEqual(build.category_visual, 1.0)

    def test_scroll_target_keeps_selection_visible(self) -> None:
        build = BuildController()
        with patch(
            "construction.BUILD_CATEGORIES",
            (("category.test", (BuildKind.SOLAR,) * 6),),
        ):
            build.enter_menu()
            for _ in range(5):
                build.menu_down()
            self.assertGreater(build.menu_scroll_target, 0.0)


class CoastOverlayTests(unittest.TestCase):
    def _world(self):
        world = generate_world(seed="COAST", size=64)
        x, y = 20, 20
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                prepare_tile(world, x + dx, y + dy)
        return world, x, y

    def test_side_rotations(self) -> None:
        world, x, y = self._world()
        expected = {
            "n": (0, -1, 270),
            "e": (1, 0, 180),
            "s": (0, 1, 90),
            "w": (-1, 0, 0),
        }
        for name, (dx, dy, rot) in expected.items():
            world, x, y = self._world()
            world.tiles[world.idx(x + dx, y + dy)] = Tile.WATER
            self.assertEqual(coast_overlay_plan(world, x, y), [("side", rot)], name)

    def test_corner_inner_and_outer(self) -> None:
        world, x, y = self._world()
        world.tiles[world.idx(x, y - 1)] = Tile.WATER
        world.tiles[world.idx(x + 1, y)] = Tile.WATER
        self.assertEqual(coast_overlay_plan(world, x, y), [("inner", 270)])

        # La diagonal en la esquina del inner no cambia el inner.
        world.tiles[world.idx(x + 1, y - 1)] = Tile.WATER
        self.assertEqual(coast_overlay_plan(world, x, y), [("inner", 270)])

        # La diagonal opuesta sí agrega el outer.
        world.tiles[world.idx(x - 1, y + 1)] = Tile.WATER
        self.assertEqual(coast_overlay_plan(world, x, y), [("inner_outer", 270)])


class CoastFullSetTests(unittest.TestCase):
    def _world(self):
        world = generate_world(seed="COASTFULL", size=64)
        x, y = 20, 20
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                prepare_tile(world, x + dx, y + dy)
        return world, x, y

    def test_u_parallel_island(self) -> None:
        cases = (
            ({"n", "e", "s"}, [("u", 0)]),
            ({"n", "e", "w"}, [("u", 90)]),
            ({"n", "s"}, [("parallel", 0)]),
            ({"e", "w"}, [("parallel", 90)]),
            ({"n", "e", "s", "w"}, [("island", 0)]),
        )
        for water, expected in cases:
            world, x, y = self._world()
            for name in water:
                dx, dy = {"n": (0, -1), "e": (1, 0), "s": (0, 1), "w": (-1, 0)}[name]
                world.tiles[world.idx(x + dx, y + dy)] = Tile.WATER
            self.assertEqual(coast_overlay_plan(world, x, y), expected, water)

    def test_inner_outer_combinations(self) -> None:
        world, x, y = self._world()
        world.tiles[world.idx(x, y - 1)] = Tile.WATER
        world.tiles[world.idx(x - 1, y)] = Tile.WATER
        world.tiles[world.idx(x - 1, y - 1)] = Tile.WATER
        world.tiles[world.idx(x + 1, y + 1)] = Tile.WATER
        self.assertEqual(
            coast_overlay_plan(world, x, y),
            [("inner_outer", 0)],
        )

    def test_single_side_with_corner_points(self) -> None:
        world, x, y = self._world()
        world.tiles[world.idx(x, y - 1)] = Tile.WATER
        world.tiles[world.idx(x + 1, y - 1)] = Tile.WATER
        world.tiles[world.idx(x - 1, y + 1)] = Tile.WATER
        self.assertEqual(
            coast_overlay_plan(world, x, y),
            [("side", 270), ("outer", 90)],
        )

    def test_diagonal_outer_only(self) -> None:
        world, x, y = self._world()
        world.tiles[world.idx(x + 1, y + 1)] = Tile.WATER
        self.assertEqual(coast_overlay_plan(world, x, y), [("outer", 180)])

    def test_l_corner_is_inner_outer(self) -> None:
        # Tierra2 del ejemplo en L: agua S/W, diagonal NE de agua.
        world, x, y = self._world()
        world.tiles[world.idx(x, y + 1)] = Tile.WATER
        world.tiles[world.idx(x - 1, y)] = Tile.WATER
        world.tiles[world.idx(x + 1, y - 1)] = Tile.WATER
        self.assertEqual(coast_overlay_plan(world, x, y), [("inner_outer", 90)])


class CableFreePlacementTests(unittest.TestCase):
    def test_cable_can_be_placed_disconnected(self) -> None:
        world = generate_world()
        sim = Simulation()
        x, y = HABITAT_X + 10, HABITAT_Y
        prepare_tile(world, x, y)
        sim.build.selected = BuildKind.CABLE
        self.assertTrue(sim.build.try_place(world, sim.resources, x, y))
        self.assertIn((x, y), world.cables)
        self.assertNotIn((x, y), get_connected(world))


class ModuleMenuTests(unittest.TestCase):
    def test_a_a_opens_menu_and_toggles(self) -> None:
        world = generate_world()
        sim = Simulation()
        mod = add_module(world, ModuleKind.FABRICATOR, 1)
        inp = Input(dev_mode=False)
        frame = FrameInput(frozenset({"A"}), frozenset({"A"}), frozenset())
        first = handle_frame_input(
            frame, inp, sim, world, layer=MapLayer.TERRAIN,
            cursor_x=mod.x, cursor_y=mod.y, select_x=None, select_y=None,
        )
        second = handle_frame_input(
            frame, inp, sim, world, layer=MapLayer.TERRAIN,
            cursor_x=mod.x, cursor_y=mod.y, select_x=first.select_x, select_y=first.select_y,
        )
        self.assertIsNotNone(sim.module_menu)
        self.assertTrue(mod.enabled)
        result = handle_frame_input(
            frame, inp, sim, world, layer=MapLayer.TERRAIN,
            cursor_x=mod.x, cursor_y=mod.y, select_x=second.select_x, select_y=second.select_y,
        )
        self.assertFalse(mod.enabled)
        self.assertIsNone(sim.module_menu)
        self.assertTrue(result.save_requested)

    def test_monitor_opens_network_screen(self) -> None:
        world = generate_world()
        sim = Simulation()
        mod = add_module(world, ModuleKind.MONITOR, 1)
        inp = Input(dev_mode=False)
        frame = FrameInput(frozenset({"A"}), frozenset({"A"}), frozenset())
        first = handle_frame_input(
            frame, inp, sim, world, layer=MapLayer.TERRAIN,
            cursor_x=mod.x, cursor_y=mod.y, select_x=None, select_y=None,
        )
        second = handle_frame_input(
            frame, inp, sim, world, layer=MapLayer.TERRAIN,
            cursor_x=mod.x, cursor_y=mod.y, select_x=first.select_x, select_y=first.select_y,
        )
        self.assertIsNotNone(sim.module_menu)
        handle_frame_input(
            frame, inp, sim, world, layer=MapLayer.TERRAIN,
            cursor_x=mod.x, cursor_y=mod.y, select_x=second.select_x, select_y=second.select_y,
        )
        self.assertTrue(sim.network_open)
        self.assertIsNone(sim.module_menu)


class MonitorTests(unittest.TestCase):
    def test_monitor_consumes_power_and_report_balances(self) -> None:
        world = generate_world()
        sim = Simulation()
        sim.day_progress = 0.5
        add_module(world, ModuleKind.MONITOR, 1)
        before = sim.resources.power
        run(sim, world, 1.0)
        self.assertAlmostEqual(before - sim.resources.power, 10.0 / 48.0, places=4)
        report = build_network_report(world, sim)
        self.assertGreaterEqual(report.balances[ResourceId.POWER].consumed, 10.0)
        self.assertGreaterEqual(report.balances[ResourceId.O2].consumed, 10.0)


class CameraBoundsTests(unittest.TestCase):
    def test_camera_reaches_full_map(self) -> None:
        world = generate_world(size=128)
        self.assertEqual(world.camera_bounds(8), (0, 0, 127, 127))


class Stage5PrepTests(unittest.TestCase):
    def _deposit(self, world, dep: Deposit, amount: float) -> None:
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                i = world.idx(HABITAT_X + 1 + dx, HABITAT_Y + dy)
                prepare_tile(world, HABITAT_X + 1 + dx, HABITAT_Y + dy)
                world.deposits[i] = dep
                world.deposit_amounts[i] = amount

    def test_coal_extractor_outputs_coal(self) -> None:
        world = generate_world()
        sim = Simulation()
        sim.day_progress = 0.5
        self._deposit(world, Deposit.COAL, 500.0)
        add_module(world, ModuleKind.COAL_EXTRACTOR, 1)
        run(sim, world, 1.0)
        self.assertAlmostEqual(sim.resources.coal, 6.0 / 48.0, places=4)

    def test_crystal_extractor_outputs_crystal(self) -> None:
        world = generate_world()
        sim = Simulation()
        sim.day_progress = 0.5
        self._deposit(world, Deposit.CRYSTAL, 500.0)
        add_module(world, ModuleKind.CRYSTAL_EXTRACTOR, 1)
        run(sim, world, 1.0)
        self.assertAlmostEqual(sim.resources.crystal, 2.0 / 48.0, places=4)

    def test_fuel_generator_burns_fuel_for_power(self) -> None:
        world = generate_world()
        sim = Simulation()
        sim.day_progress = 0.5
        sim.resources.fuel = 10.0
        sim.resources.power = 10.0
        add_module(world, ModuleKind.FUEL_GENERATOR, 1)
        before = sim.resources.power
        run(sim, world, 1.0)
        self.assertAlmostEqual(10.0 - sim.resources.fuel, 1.0 / 48.0, places=4)
        self.assertGreater(sim.resources.power, before)

    def test_deposit_preview_for_coal_and_crystal(self) -> None:
        world = generate_world()
        sim = Simulation()
        x, y = HABITAT_X + 1, HABITAT_Y
        prepare_tile(world, x, y)
        sim.resources.mineral = 10.0
        sim.build.selected = BuildKind.COAL_EXTRACTOR
        self.assertEqual(sim.build.preview(world, sim.resources, x, y), BuildPreview.NO_DEPOSIT)
        i = world.idx(x, y)
        world.deposits[i] = Deposit.COAL
        world.deposit_amounts[i] = 100.0
        self.assertEqual(sim.build.preview(world, sim.resources, x, y), BuildPreview.OK)
