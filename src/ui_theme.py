"""Paleta, layout 640×480 y utilidades de formato para la UI."""

from __future__ import annotations

import pygame

from config import (
    BOTTOM_BAR_H,
    PANEL_W,
    SCREEN_H,
    SCREEN_W,
    TOP_BAR_H,
)
from resources import AlertLevel
from world import Deposit, Tile

# Colores retro CRT
COL_PANEL = (18, 28, 20)
COL_BORDER = (50, 130, 70)
COL_TEXT = (80, 255, 120)
COL_DIM = (45, 110, 60)
COL_WARN = (255, 200, 60)
COL_CRITICAL = (255, 80, 70)
COL_CURSOR = (255, 255, 180)
COL_HABITAT = (220, 200, 80)
COL_SOLAR = (255, 140, 40)
COL_RADAR = (80, 220, 220)
COL_EXTRACTOR = (60, 150, 230)
COL_GREENHOUSE = (90, 200, 70)
COL_MINE = (140, 110, 75)
COL_FABRICATOR = (200, 120, 180)
COL_STORAGE = (170, 170, 90)
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

MODULE_COLORS = {
    "habitat": COL_HABITAT,
    "solar": COL_SOLAR,
    "radar": COL_RADAR,
    "extractor": COL_EXTRACTOR,
    "greenhouse": COL_GREENHOUSE,
    "mine": COL_MINE,
    "fabricator": COL_FABRICATOR,
    "storage": COL_STORAGE,
}

DEPOSIT_OVERLAY_ALPHA = 0.55


def map_rect() -> pygame.Rect:
    return pygame.Rect(0, TOP_BAR_H, SCREEN_W - PANEL_W, SCREEN_H - TOP_BAR_H - BOTTOM_BAR_H)


def panel_rect() -> pygame.Rect:
    h = SCREEN_H - TOP_BAR_H - BOTTOM_BAR_H
    return pygame.Rect(SCREEN_W - PANEL_W, TOP_BAR_H, PANEL_W, h)


def alert_color(level: AlertLevel) -> tuple[int, int, int]:
    if level == AlertLevel.CRITICAL:
        return COL_CRITICAL
    if level == AlertLevel.WARNING:
        return COL_WARN
    return COL_DIM


def format_amount(value: float) -> str:
    return f"{value:.1f}"


def format_days(days: float) -> str:
    if days >= 100:
        return "99+"
    return f"{days:.1f}"
