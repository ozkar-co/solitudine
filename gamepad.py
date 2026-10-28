"""Input semántico del mando R36S — la UI usa estos nombres, no ejes."""

from __future__ import annotations

import pygame

DEADZONE = 0.15

# Botones físicos (btn index -> nombre)
BUTTONS: dict[int, str] = {
    0: "A",
    1: "B",
    2: "X",
    3: "Y",
    4: "L1",
    5: "R1",
    6: "L2",
    7: "R2",
    8: "SELECT",
    9: "START",
    11: "L3",
    12: "R3",
    13: "FN",
    14: "DPAD_UP",
    15: "DPAD_DOWN",
    16: "DPAD_LEFT",
    17: "DPAD_RIGHT",
}

LJOY_UP = "LJOY_UP"
LJOY_DOWN = "LJOY_DOWN"
LJOY_LEFT = "LJOY_LEFT"
LJOY_RIGHT = "LJOY_RIGHT"

RJOY_UP = "RJOY_UP"
RJOY_DOWN = "RJOY_DOWN"
RJOY_LEFT = "RJOY_LEFT"
RJOY_RIGHT = "RJOY_RIGHT"

LJOY_ACTIONS = (LJOY_UP, LJOY_DOWN, LJOY_LEFT, LJOY_RIGHT)
RJOY_ACTIONS = (RJOY_UP, RJOY_DOWN, RJOY_LEFT, RJOY_RIGHT)
STICK_ACTIONS = LJOY_ACTIONS + RJOY_ACTIONS

# --- Mapeo hardware (solo aquí) ---
# Stick izq: X=ax0, Y=ax3 (arriba negativo)
# Stick der: X=ax2 (derecha negativo), Y=ax1 (arriba positivo)


def _read_left_stick(joy: pygame.joystick.Joystick) -> set[str]:
    actions: set[str] = set()
    x = joy.get_axis(0)
    y = joy.get_axis(3)
    if y < -DEADZONE:
        actions.add(LJOY_UP)
    if y > DEADZONE:
        actions.add(LJOY_DOWN)
    if x < -DEADZONE:
        actions.add(LJOY_LEFT)
    if x > DEADZONE:
        actions.add(LJOY_RIGHT)
    return actions


def _read_right_stick(joy: pygame.joystick.Joystick) -> set[str]:
    actions: set[str] = set()
    x = joy.get_axis(2)
    y = joy.get_axis(1)
    if y > DEADZONE:
        actions.add(RJOY_UP)
    if y < -DEADZONE:
        actions.add(RJOY_DOWN)
    if x < -DEADZONE:
        actions.add(RJOY_RIGHT)
    if x > DEADZONE:
        actions.add(RJOY_LEFT)
    return actions


def read_actions(
    joy: pygame.joystick.Joystick,
    held_buttons: set[int],
) -> frozenset[str]:
    """Estado completo de un mando: botones + sticks como nombres estándar."""
    actions: set[str] = set()
    for btn in held_buttons:
        name = BUTTONS.get(btn)
        if name:
            actions.add(name)
    actions |= _read_left_stick(joy)
    actions |= _read_right_stick(joy)
    return frozenset(actions)


def diff_actions(
    joy_index: int,
    prev: frozenset[str],
    curr: frozenset[str],
) -> list[str]:
    logs: list[str] = []
    for name in sorted(prev - curr):
        logs.append(f"UP    j{joy_index} {name}")
    for name in sorted(curr - prev):
        logs.append(f"DOWN  j{joy_index} {name}")
    return logs


def format_actions(actions: frozenset[str]) -> str:
    if not actions:
        return "-"
    return ", ".join(sorted(actions))
