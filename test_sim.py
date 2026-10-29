"""Tests mínimos de regresión: apagado y consumo de lámpara."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from config import HABITAT_X, HABITAT_Y
from construction import BuildController, BuildKind, BuildMode, kind_locked
from credits import CREDITS_SCROLL_STEP
from game_input import handle_frame_input
from input_state import FrameInput, Input
from logistics import network_caps
from materials import Stockpile
from module_defs import buffer_cap, module_active
from module_kind import ModuleKind
from module_power import module_energy_daily
from network import get_connected, invalidate_network_cache
from resources import AlertLevel, ResourceId, ResourcePool
from savegame import delete_save, load_game, save_game
from simulation import Simulation
from vision import on_module_built
from ui import MapLayer
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
    def test_depleted_extractor_does_not_consume_power(self) -> None:
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
        self.assertAlmostEqual(before - sim.resources.power, 8.0 / 48.0, places=4)


class EnabledTests(unittest.TestCase):
    def test_disabled_fabricator_stops(self) -> None:
        world = generate_world()
        sim = Simulation()
        sim.day_progress = 0.5
        sim.stock.mineral = 100.0
        fab = add_module(world, ModuleKind.FABRICATOR, 1)
        before = sim.stock.components

        run(sim, world, 2.0)
        self.assertGreater(sim.stock.components, before)

        fab.enabled = False
        before = sim.stock.components
        run(sim, world, 2.0)
        self.assertEqual(sim.stock.components, before)

    def test_disabled_storage_loses_cap(self) -> None:
        world = generate_world()
        storage = add_module(world, ModuleKind.STORAGE, 1)
        active_cap = network_caps(world).components
        storage.enabled = False
        self.assertLess(network_caps(world).components, active_cap)

    def test_habitat_stays_active(self) -> None:
        world = generate_world()
        habitat = world.module_at(HABITAT_X, HABITAT_Y)
        habitat.enabled = False
        self.assertTrue(module_active(habitat, True))


class CableNetworkTests(unittest.TestCase):
    def test_module_accepts_cables_on_all_four_sides(self) -> None:
        world = generate_world()
        stock = Stockpile(components=10.0)
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
        sim.stock.components = 0.0
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


class SaveTests(unittest.TestCase):
    def test_roundtrip(self) -> None:
        world = generate_world()
        sim = Simulation()
        sim.day = 2
        sim.day_progress = 0.42
        sim.stock.components = 31.0
        fab = add_module(world, ModuleKind.FABRICATOR, 1, enabled=False)
        fab.built_day = 3
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
            self.assertEqual(sim2.stock.components, 31.0)
            self.assertEqual(sim2.resources.power, 33.0)
            mod = world2.module_at(fab.x, fab.y)
            self.assertIsNotNone(mod)
            self.assertFalse(mod.enabled)
            self.assertEqual(mod.built_day, 3)
            self.assertEqual(world2.module_at(lamp.x, lamp.y).kind, ModuleKind.LAMP)
            self.assertEqual(sim2.research.unlocked, {"condensador"})
            self.assertEqual(sim2.research.active, "electrolisis")
            self.assertAlmostEqual(sim2.research.progress, 0.5)
            delete_save(path)
            self.assertIsNone(load_game(path))


    def test_v1_loads_without_research(self) -> None:
        world = generate_world()
        sim = Simulation()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "save.json"
            save_game(world, sim, path)
            data = json.loads(path.read_text(encoding="utf-8"))
            data["version"] = 1
            data["sim"].pop("research")
            path.write_text(json.dumps(data), encoding="utf-8")
            loaded = load_game(path)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded[1].research.unlocked, set())


class ResearchTests(unittest.TestCase):
    def test_research_spends_and_completes(self) -> None:
        world = generate_world()
        sim = Simulation()
        sim.day_progress = 0.5
        lab = add_module(world, ModuleKind.LABORATORY, 1)
        before = sim.stock.components
        self.assertTrue(sim.start_research(world))
        self.assertEqual(sim.stock.components, before - 4.0)
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
        before = sim.stock.components
        self.assertFalse(sim.start_research(world))
        self.assertEqual(sim.stock.components, before)

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


if __name__ == "__main__":
    unittest.main()
