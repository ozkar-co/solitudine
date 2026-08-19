"""Materiales de construcción (stock del hábitat)."""

from __future__ import annotations

from dataclasses import dataclass

from config import INITIAL_COMPONENTS


@dataclass
class Stockpile:
    components: float = INITIAL_COMPONENTS

    def can_afford(self, cost: float) -> bool:
        return self.components >= cost

    def spend(self, cost: float) -> bool:
        if not self.can_afford(cost):
            return False
        self.components -= cost
        return True
