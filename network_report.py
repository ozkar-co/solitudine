"""Resumen de producción/consumo de la red para la estación de monitoreo."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING

from config import HOURS_PER_DAY
from logistics import network_caps
from module_defs import ModuleContext, effective_flow, module_active
from network import get_connected
from resources import RESOURCES, ResourceId
from world import ModuleState, World

if TYPE_CHECKING:
    from simulation import Simulation


@dataclass(frozen=True)
class ResourceBalance:
    produced: float
    consumed: float

    @property
    def net(self) -> float:
        return self.produced - self.consumed


@dataclass(frozen=True)
class NetworkReport:
    balances: dict[ResourceId, ResourceBalance]
    caps: dict[ResourceId, float]
    counts: Counter
    power_factor: float


def build_network_report(world: World, sim: "Simulation") -> NetworkReport:
    connected = get_connected(world)
    caps = network_caps(world, connected)
    resource_ids = tuple(definition.id for definition in RESOURCES)
    produced = {resource: 0.0 for resource in resource_ids}
    consumed = {resource: 0.0 for resource in resource_ids}
    counts: Counter = Counter()
    hour_float = sim.day_progress * HOURS_PER_DAY

    for mod in world.modules:
        counts[mod.state] += 1
        if not module_active(mod, (mod.x, mod.y) in connected):
            continue
        ctx = ModuleContext(world=world, hour_float=hour_float, connected=True)
        flow = effective_flow(mod, ctx)
        for resource in resource_ids:
            value = getattr(flow, resource.value, 0.0)
            if value > 0.0:
                produced[resource] += value
            elif value < 0.0:
                consumed[resource] -= value

    balances = {
        resource: ResourceBalance(produced[resource], consumed[resource])
        for resource in resource_ids
    }
    return NetworkReport(
        balances=balances,
        caps=caps,
        counts=counts,
        power_factor=sim.power_factor,
    )


def module_count(report: NetworkReport, state: ModuleState) -> int:
    return int(report.counts.get(state, 0))
