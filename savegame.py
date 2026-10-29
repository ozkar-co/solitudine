"""Guardado JSON mínimo — simulación + mundo comprimido."""

from __future__ import annotations

import base64
import json
import os
import zlib
from array import array
from dataclasses import asdict
from pathlib import Path

from materials import Stockpile
from module_kind import ModuleKind
from resources import ResourcePool
from simulation import Simulation
from world import Module, ModuleState, World, generate_world

SAVE_PATH = Path(__file__).resolve().parent / "save.json"
VERSION = 3


def _pack(data: bytes) -> str:
    return base64.b64encode(zlib.compress(data, 6)).decode("ascii")


def _unpack(text: str) -> bytes:
    return zlib.decompress(base64.b64decode(text))


def _save_data(world: World, sim: Simulation) -> dict:
    amounts = array("f", world.deposit_amounts).tobytes()
    return {
        "version": VERSION,
        "sim": {
            "day": sim.day,
            "day_progress": sim.day_progress,
            "resources": asdict(sim.resources),
            "stock": asdict(sim.stock),
            "game_over": sim.game_over,
            "death_cause": sim.death_cause,
            "research": {
                "unlocked": sorted(sim.research.unlocked),
                "active": sim.research.active,
                "progress": sim.research.progress,
            },
        },
        "world": {
            "size": world.size,
            "expl_min_x": world.expl_min_x,
            "expl_min_y": world.expl_min_y,
            "expl_max_x": world.expl_max_x,
            "expl_max_y": world.expl_max_y,
            "explored_version": world.explored_version,
            "tiles": _pack(bytes(world.tiles)),
            "deposits": _pack(bytes(world.deposits)),
            "amounts": _pack(amounts),
            "explored": _pack(bytes(world.explored)),
            "visible": _pack(bytes(world.visible)),
            "visible_count": _pack(world.visible_count.tobytes()),
            "modules": [
                {
                    "kind": mod.kind.value,
                    "x": mod.x,
                    "y": mod.y,
                    "state": int(mod.state),
                    "enabled": mod.enabled,
                    "build_progress": mod.build_progress,
                    "build_total": mod.build_total,
                    "buffer": mod.buffer,
                    "buffer_cap": mod.buffer_cap,
                    "shadow_stamped": mod.shadow_stamped,
                    "clear_active": mod.clear_active,
                    "built_day": mod.built_day,
                }
                for mod in world.modules
            ],
            "cables": [[x, y] for x, y in world.cables],
        },
    }


def save_game(world: World, sim: Simulation, path: Path = SAVE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(_save_data(world, sim), separators=(",", ":")), encoding="utf-8")
    os.replace(tmp, path)


def delete_save(path: Path = SAVE_PATH) -> None:
    path.unlink(missing_ok=True)


def load_game(path: Path = SAVE_PATH) -> tuple[World, Simulation] | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    version = data.get("version")
    if version not in (1, 2, VERSION):
        raise ValueError("Versión de guardado incompatible")

    wd = data["world"]
    world = generate_world()
    if wd["size"] != world.size:
        raise ValueError("Tamaño de mapa incompatible")
    n = world.size * world.size

    tiles = list(_unpack(wd["tiles"]))
    deposits = list(_unpack(wd["deposits"]))
    amounts = list(array("f", _unpack(wd["amounts"])))
    explored = bytearray(_unpack(wd["explored"]))
    visible = bytearray(_unpack(wd["visible"]))
    visible_count = array("H")
    visible_count.frombytes(_unpack(wd["visible_count"]))
    if not (
        len(tiles) == n
        and len(deposits) == n
        and len(amounts) == n
        and len(explored) == n
        and len(visible) == n
        and len(visible_count) == n
    ):
        raise ValueError("Mapa corrupto")

    world.tiles = tiles
    world.deposits = deposits
    world.deposit_amounts = amounts
    world.explored = explored
    world.visible = visible
    world.visible_count = visible_count
    world.expl_min_x = wd["expl_min_x"]
    world.expl_min_y = wd["expl_min_y"]
    world.expl_max_x = wd["expl_max_x"]
    world.expl_max_y = wd["expl_max_y"]
    world.explored_version = wd["explored_version"]
    world.modules = []
    world.module_cells = {}
    for raw in wd["modules"]:
        mod = Module(
            kind=ModuleKind(raw["kind"]),
            x=raw["x"],
            y=raw["y"],
            state=ModuleState(raw["state"]),
            enabled=raw["enabled"],
            build_progress=raw["build_progress"],
            build_total=raw["build_total"],
            buffer=raw["buffer"],
            buffer_cap=raw["buffer_cap"],
            shadow_stamped=raw["shadow_stamped"],
            clear_active=raw["clear_active"],
            built_day=raw.get("built_day", 0),
        )
        world.modules.append(mod)
        world.module_cells[(mod.x, mod.y)] = mod
    world.cables = {(x, y) for x, y in wd["cables"]}
    world.invalidate_network_cache()

    sd = data["sim"]
    resources = dict(sd["resources"])
    if version < 3:
        # En v1/v2 los campos diarios eran consumo bruto (positivo).
        for key in ("o2_daily", "power_daily", "water_daily", "food_daily"):
            value = float(resources.get(key, 0.0))
            if value > 0.0:
                resources[key] = -value
    sim = Simulation(
        day=sd["day"],
        day_progress=sd["day_progress"],
        resources=ResourcePool(**resources),
        stock=Stockpile(**sd["stock"]),
    )
    sim.game_over = bool(sd.get("game_over", False))
    sim.death_cause = sd.get("death_cause", "")
    sim.paused = sim.game_over
    rd = sd.get("research", {})
    sim.research.unlocked = set(rd.get("unlocked", ()))
    sim.research.active = rd.get("active")
    sim.research.progress = float(rd.get("progress", 0.0))
    return world, sim
