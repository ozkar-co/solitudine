"""Emulación de mando con teclado — solo SOLITUDINE_DEV=1 en PC."""

import os

import pygame

from gamepad import diff_actions

DEV_JOY = 0

KEY_TO_ACTION: dict[int, str] = {
    pygame.K_z: "A",
    pygame.K_x: "B",
    pygame.K_c: "X",
    pygame.K_v: "Y",
    pygame.K_q: "L1",
    pygame.K_e: "R1",
    pygame.K_1: "L2",
    pygame.K_2: "R2",
    pygame.K_BACKSPACE: "SELECT",
    pygame.K_RETURN: "START",
    pygame.K_u: "L3",
    pygame.K_o: "R3",
    pygame.K_f: "FN",
    pygame.K_i: "DPAD_UP",
    pygame.K_k: "DPAD_DOWN",
    pygame.K_j: "DPAD_LEFT",
    pygame.K_l: "DPAD_RIGHT",
    pygame.K_w: "LJOY_UP",
    pygame.K_s: "LJOY_DOWN",
    pygame.K_a: "LJOY_LEFT",
    pygame.K_d: "LJOY_RIGHT",
    pygame.K_UP: "RJOY_UP",
    pygame.K_DOWN: "RJOY_DOWN",
    pygame.K_LEFT: "RJOY_LEFT",
    pygame.K_RIGHT: "RJOY_RIGHT",
}

ALL_DEV_KEYS = frozenset(KEY_TO_ACTION)

DEV_KEYMAP = """
DEV teclado -> mando
Z=A  X=B  C=X  V=Y   Q=L1  E=R1  1=L2  2=R2
Bksp=SELECT  Enter=START  U=L3  O=R3  F=FN
IJKL=DPAD   WASD=LJOY   Flechas=RJOY
SELECT+START (Bksp+Enter)=salir
""".strip()


def setup_dev_env() -> None:
    os.environ.setdefault("SDL_HINT_GRAB_KEYBOARD", "1")


def setup_dev_display() -> None:
    pygame.event.set_grab(True)


class DevKeyboard:
    def __init__(self) -> None:
        self._keys: set[int] = set()
        self._prev: frozenset[str] = frozenset()

    def on_event(self, event: pygame.event.Event) -> list[str]:
        if event.type == pygame.KEYDOWN and event.key in ALL_DEV_KEYS:
            self._keys.add(event.key)
        elif event.type == pygame.KEYUP and event.key in ALL_DEV_KEYS:
            self._keys.discard(event.key)
        else:
            return []
        return self._sync()

    def tick(self) -> tuple[frozenset[str], list[str]]:
        pressed = pygame.key.get_pressed()
        synced = {k for k in ALL_DEV_KEYS if pressed[k]}
        if synced == self._keys and self._prev:
            return self._prev, []
        self._keys = synced
        return self._sync()

    def _actions(self) -> frozenset[str]:
        return frozenset(KEY_TO_ACTION[k] for k in self._keys)

    def _sync(self) -> tuple[frozenset[str], list[str]]:
        curr = self._actions()
        logs = diff_actions(DEV_JOY, self._prev, curr)
        self._prev = curr
        return curr, logs
