"""Balance energético por módulo (panel) — delegado a module_defs."""

from __future__ import annotations

from module_defs import ModuleContext, panel_power_daily as _panel_power_daily
from world import Module, World


def module_energy_daily(
    mod: Module,
    world: World | None = None,
    *,
    hour_float: float = 12.0,
    connected: bool = True,
) -> float:
    ctx = ModuleContext(world=world, hour_float=hour_float, connected=connected)
    return _panel_power_daily(mod, ctx)


def format_energy_daily(value: float) -> str:
    if value > 0:
        return f"+{value:.1f}"
    return f"{value:.1f}"
