"""Materiales de construcción (stock del hábitat / red)."""

from __future__ import annotations

from dataclasses import dataclass

from config import INITIAL_COMPONENTS


@dataclass
class Stockpile:
    components: float = INITIAL_COMPONENTS
    mineral: float = 0.0

    def can_afford(self, cost: float) -> bool:
        return self.components >= cost

    def spend(self, cost: float) -> bool:
        if not self.can_afford(cost):
            return False
        self.components -= cost
        return True
