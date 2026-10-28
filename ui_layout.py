"""Regiones fijas de la UI — 640×480 sobre una grilla de 16 px."""

from __future__ import annotations

import pygame

from config import BOTTOM_BAR_H, PANEL_W, SCREEN_H, SCREEN_W, TOP_BAR_H


def top_bar_rect() -> pygame.Rect:
    return pygame.Rect(0, 0, SCREEN_W, TOP_BAR_H)


def bottom_bar_rect() -> pygame.Rect:
    return pygame.Rect(0, SCREEN_H - BOTTOM_BAR_H, SCREEN_W, BOTTOM_BAR_H)


def panel_rect() -> pygame.Rect:
    h = SCREEN_H - TOP_BAR_H - BOTTOM_BAR_H
    return pygame.Rect(SCREEN_W - PANEL_W, TOP_BAR_H, PANEL_W, h)


def map_rect() -> pygame.Rect:
    return pygame.Rect(0, TOP_BAR_H, SCREEN_W - PANEL_W, SCREEN_H - TOP_BAR_H - BOTTOM_BAR_H)
