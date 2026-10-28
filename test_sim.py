"""Tests mínimos de regresión: apagado y consumo de lámpara."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from config import HABITAT_X, HABITAT_Y
from logistics import network_caps
from module_defs import buffer_cap, module_active
from module_kind import ModuleKind
from module_power import module_energy_daily
from network import get_connected, invalidate_network_cache
from savegame import delete_save, load_game, save_game
from simulation import Simulation
from vision import on_module_built
from ui_night import light_sources
from world import Module, ModuleState, generate_world


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


class EnabledTests(unittest.TestCase):
    def test_disabled_fabricator_stops(self) -> None:
        world = generate_world()
        sim = Simulation()
        sim.day_progress = 0.5
        sim.stock.mineral = 100.0
        fab = add_module(world, ModuleKind.FABRICATOR, 1)

        run(sim, world, 2.0)
        self.assertGreater(sim.stock.components, 42.0)

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


class SaveTests(unittest.TestCase):
    def test_roundtrip(self) -> None:
        world = generate_world()
        sim = Simulation()
        sim.day = 2
        sim.day_progress = 0.42
        sim.stock.components = 31.0
        fab = add_module(world, ModuleKind.FABRICATOR, 1, enabled=False)
        lamp = add_module(world, ModuleKind.LAMP, 2)
        sim.resources.power = 33.0

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
            self.assertEqual(world2.module_at(lamp.x, lamp.y).kind, ModuleKind.LAMP)
            delete_save(path)
            self.assertIsNone(load_game(path))


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


if __name__ == "__main__":
    unittest.main()
