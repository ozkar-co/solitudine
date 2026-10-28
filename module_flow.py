"""Flujos diarios por módulo (panel) — delegado a module_defs."""

from __future__ import annotations

from module_defs import ModuleContext, panel_flow_lines as _panel_flow_lines
from world import Module, World


def module_flow_lines(
    mod: Module,
    world: World | None = None,
    *,
    hour_float: float = 12.0,
    connected: bool = True,
) -> list[tuple[str, float]]:
    ctx = ModuleContext(world=world, hour_float=hour_float, connected=connected)
    return _panel_flow_lines(mod, ctx)
