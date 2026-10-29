"""Paleta y utilidades de formato para la UI."""

from __future__ import annotations

from i18n import t
from resources import RESOURCE_BY_ID, AlertLevel, Cost
from world import Deposit, Tile

from ui_layout import map_rect, panel_rect

COL_PANEL = (18, 28, 20)
COL_BORDER = (50, 130, 70)
COL_TEXT = (80, 255, 120)
COL_DIM = (45, 110, 60)
COL_WARN = (255, 200, 60)
COL_CRITICAL = (255, 80, 70)
COL_CURSOR = (255, 255, 180)
COL_CABLE = (255, 230, 80)
COL_FOG = (20, 32, 24)
COL_PREVIEW_OK = (120, 255, 160)
COL_PREVIEW_BAD = (255, 100, 90)

TILE_COLORS = {
    Tile.GROUND: (55, 85, 45),
    Tile.WATER: (35, 75, 130),
    Tile.ROCK: (85, 88, 92),
}

DEPOSIT_OVERLAY = {
    Deposit.WATER: (40, 90, 160),
    Deposit.MINERAL: (120, 95, 55),
}

DEPOSIT_OVERLAY_ALPHA = 0.55


def alert_color(level: AlertLevel) -> tuple[int, int, int]:
    if level == AlertLevel.CRITICAL:
        return COL_CRITICAL
    if level == AlertLevel.WARNING:
        return COL_WARN
    return COL_DIM


def format_amount(value: float) -> str:
    if value <= 0.0:
        return "0.0"
    if value < 0.1:
        return f"{value:.2f}"
    return f"{value:.1f}"


def format_days(days: float) -> str:
    if days == float("inf"):
        return "est."
    if days >= 100:
        return "99+d"
    return f"{days:.1f}d"


def format_cost_text(cost: Cost) -> str:
    parts = []
    for resource, amount in cost.items():
        defn = RESOURCE_BY_ID[resource]
        parts.append(f"{format_amount(amount)} {t(defn.short_key)}")
    return " + ".join(parts)
