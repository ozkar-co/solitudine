"""Contadores de la partida — datos simples, sin lógica."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Stats:
    scrap_collected: float = 0.0
    scrap_processed: float = 0.0
    mineral_from_scrap: float = 0.0
    components_from_scrap: float = 0.0
