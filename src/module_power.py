"""Balance energético por módulo (E/día)."""

from __future__ import annotations

from config import (
    EXTRACTOR_POWER_DAILY,
    GREENHOUSE_POWER_DAILY,
    HABITAT_POWER_DAILY,
    RADAR_POWER_DAILY,
    SOLAR_POWER_DAILY,
)
from world import Module, ModuleState


def module_energy_daily(mod: Module) -> float:
    """Negativo = consume, positivo = produce, 0 = inactivo."""
    if mod.kind == "habitat":
        return -HABITAT_POWER_DAILY
    if mod.kind == "radar":
        return -RADAR_POWER_DAILY if mod.state == ModuleState.ONLINE else 0.0
    if mod.kind == "solar":
        return SOLAR_POWER_DAILY if mod.state == ModuleState.ONLINE else 0.0
    if mod.kind == "extractor":
        return -EXTRACTOR_POWER_DAILY if mod.state == ModuleState.ONLINE else 0.0
    if mod.kind == "greenhouse":
        return -GREENHOUSE_POWER_DAILY if mod.state == ModuleState.ONLINE else 0.0
    return 0.0


def format_energy_daily(value: float) -> str:
    if value > 0:
        return f"+{value:.1f}"
    return f"{value:.1f}"
