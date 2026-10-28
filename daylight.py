"""Curva de luz natural compartida por simulación y render."""

from __future__ import annotations

from config import HOURS_PER_DAY


def natural_light(day_progress: float) -> float:
    """Luz natural 0..1; día pleno 1, noche 0, rampas en alba/ocaso."""
    hour = (day_progress % 1.0) * HOURS_PER_DAY
    if 7.0 <= hour < 17.0:
        return 1.0
    if 17.0 <= hour < 20.0:
        return 1.0 - (hour - 17.0) / 3.0
    if 4.0 <= hour < 7.0:
        return (hour - 4.0) / 3.0
    return 0.0


def darkness(day_progress: float) -> float:
    return 1.0 - natural_light(day_progress)
