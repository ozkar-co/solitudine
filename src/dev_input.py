"""Emulación de mando con teclado — solo SOLITUDINE_DEV=1 en PC."""

import os

import pygame

from gamepad import (
    LEFT_STICK_X,
    LEFT_STICK_Y,
    RIGHT_STICK_X,
    RIGHT_STICK_Y,
    axis_active,
    button_name,
)

DEV_JOY = 0
NUM_AXES = 4

KEY_TO_BTN: dict[int, int] = {
    pygame.K_z: 0,
    pygame.K_x: 1,
    pygame.K_c: 2,
    pygame.K_v: 3,
    pygame.K_q: 4,
    pygame.K_e: 5,
    pygame.K_1: 6,
    pygame.K_2: 7,
    pygame.K_BACKSPACE: 8,
    pygame.K_RETURN: 9,
    pygame.K_u: 11,
    pygame.K_o: 12,
    pygame.K_f: 13,
    pygame.K_i: 14,
    pygame.K_k: 15,
    pygame.K_j: 16,
    pygame.K_l: 17,
}

STICK_KEYS = frozenset(
    {
        pygame.K_w,
        pygame.K_a,
        pygame.K_s,
        pygame.K_d,
        pygame.K_UP,
        pygame.K_DOWN,
        pygame.K_LEFT,
        pygame.K_RIGHT,
    }
)

ALL_DEV_KEYS = frozenset(KEY_TO_BTN) | STICK_KEYS


class DevPadState:
    __slots__ = ("held", "axes")

    def __init__(self) -> None:
        self.held: dict[int, int] = {}
        self.axes: dict[int, float] = {i: 0.0 for i in range(NUM_AXES)}


def setup_dev_env() -> None:
    os.environ.setdefault("SDL_HINT_GRAB_KEYBOARD", "1")


def setup_dev_display() -> None:
    pygame.event.set_grab(True)


def _axes_from_keys(keys: set[int]) -> dict[int, float]:
    axes = {i: 0.0 for i in range(NUM_AXES)}

    x = float(pygame.K_d in keys) - float(pygame.K_a in keys)
    y = float(pygame.K_s in keys) - float(pygame.K_w in keys)
    if x:
        axes[LEFT_STICK_X] = x
    if y:
        axes[LEFT_STICK_Y] = y

    rx = float(pygame.K_LEFT in keys) - float(pygame.K_RIGHT in keys)
    ry = float(pygame.K_UP in keys) - float(pygame.K_DOWN in keys)
    if rx:
        axes[RIGHT_STICK_X] = rx
    if ry:
        axes[RIGHT_STICK_Y] = ry

    return axes


class DevKeyboard:
    def __init__(self) -> None:
        self._keys: set[int] = set()
        self._prev: DevPadState | None = None

    def on_event(self, event: pygame.event.Event) -> list[str]:
        if event.type == pygame.KEYDOWN and event.key in ALL_DEV_KEYS:
            self._keys.add(event.key)
        elif event.type == pygame.KEYUP and event.key in ALL_DEV_KEYS:
            self._keys.discard(event.key)
        else:
            return []

        state = self._build_state()
        logs = self._diff(self._prev, state)
        self._prev = state
        return logs

    def tick(self) -> tuple[DevPadState, list[str]]:
        pressed = pygame.key.get_pressed()
        synced = {k for k in ALL_DEV_KEYS if pressed[k]}
        if synced != self._keys:
            self._keys = synced
            state = self._build_state()
            logs = self._diff(self._prev, state)
            self._prev = state
            return state, logs
        if self._prev is None:
            state = self._build_state()
            self._prev = state
            return state, []
        return self._prev, []

    def _build_state(self) -> DevPadState:
        state = DevPadState()
        for key in self._keys:
            btn = KEY_TO_BTN.get(key)
            if btn is not None:
                state.held[btn] = btn
        state.axes = _axes_from_keys(self._keys)
        return state

    def _diff(self, prev: DevPadState | None, state: DevPadState) -> list[str]:
        if prev is None:
            return []
        logs: list[str] = []
        for btn in set(prev.held) - set(state.held):
            logs.append(f"UP    j{DEV_JOY} {button_name(btn)}")
        for btn in set(state.held) - set(prev.held):
            logs.append(f"DOWN  j{DEV_JOY} {button_name(btn)}")
        for ax, val in state.axes.items():
            old = prev.axes.get(ax, 0.0)
            if axis_active(val) and not axis_active(old):
                logs.append(f"AXIS  j{DEV_JOY} ax{ax} {val:+.2f}")
            elif not axis_active(val) and axis_active(old):
                logs.append(f"AXIS  j{DEV_JOY} ax{ax} {val:+.2f}")
        return logs

    @property
    def state(self) -> DevPadState:
        if self._prev is None:
            self._prev = self._build_state()
        return self._prev


HELP = "Clic ventana  |  WASD/flechas  ZXCV=ABXY  IJKL=cruceta"
