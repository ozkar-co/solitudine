"""Entrada unificada: held, pressed, released."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from gamepad import (
    LJOY_DOWN,
    LJOY_LEFT,
    LJOY_RIGHT,
    LJOY_UP,
    RJOY_DOWN,
    RJOY_LEFT,
    RJOY_RIGHT,
    RJOY_UP,
    read_actions,
)


@dataclass
class FrameInput:
    held: frozenset[str]
    pressed: frozenset[str]
    released: frozenset[str]


CURSOR_ACTIONS = {
    LJOY_UP,
    LJOY_DOWN,
    LJOY_LEFT,
    LJOY_RIGHT,
    "DPAD_UP",
    "DPAD_DOWN",
    "DPAD_LEFT",
    "DPAD_RIGHT",
}

PAN_ACTIONS = {RJOY_UP, RJOY_DOWN, RJOY_LEFT, RJOY_RIGHT}


class Input:
    def __init__(self, dev_mode: bool) -> None:
        self.dev_mode = dev_mode
        self._prev: frozenset[str] = frozenset()
        self._held_btns: dict[tuple[int, int], int] = {}
        self._joysticks: list[pygame.joystick.Joystick] = []
        self._dev_kb = None
        if dev_mode:
            from dev_input import DevKeyboard

            self._dev_kb = DevKeyboard()

    def open_joysticks(self) -> None:
        if self.dev_mode:
            return
        for i in range(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(i)
            joy.init()
            self._joysticks.append(joy)

    @property
    def dev_keyboard(self):
        return self._dev_kb

    def process_event(self, event: pygame.event.Event) -> None:
        if self.dev_mode and self._dev_kb and event.type in (
            pygame.KEYDOWN,
            pygame.KEYUP,
        ):
            self._dev_kb.on_event(event)
            return
        if event.type == pygame.JOYBUTTONDOWN:
            self._held_btns[(event.joy, event.button)] = event.button
        elif event.type == pygame.JOYBUTTONUP:
            self._held_btns.pop((event.joy, event.button), None)
        elif event.type == pygame.JOYDEVICEADDED:
            joy = pygame.joystick.Joystick(event.device_index)
            joy.init()
            self._joysticks.append(joy)

    def poll(self) -> FrameInput:
        if self.dev_mode and self._dev_kb:
            held, _ = self._dev_kb.tick()
        elif self._joysticks:
            buttons = {b for (_, b) in self._held_btns}
            held = read_actions(self._joysticks[0], buttons)
        else:
            held = frozenset()

        pressed = held - self._prev
        released = self._prev - held
        self._prev = held
        return FrameInput(held=held, pressed=pressed, released=released)

    def cursor_delta(self, inp: FrameInput) -> tuple[int, int]:
        dx = dy = 0
        if LJOY_LEFT in inp.held or "DPAD_LEFT" in inp.held:
            dx -= 1
        if LJOY_RIGHT in inp.held or "DPAD_RIGHT" in inp.held:
            dx += 1
        if LJOY_UP in inp.held or "DPAD_UP" in inp.held:
            dy -= 1
        if LJOY_DOWN in inp.held or "DPAD_DOWN" in inp.held:
            dy += 1
        return dx, dy

    def pan_delta(self, inp: FrameInput) -> tuple[float, float]:
        dx = dy = 0.0
        if RJOY_LEFT in inp.held:
            dx -= 1
        if RJOY_RIGHT in inp.held:
            dx += 1
        if RJOY_UP in inp.held:
            dy -= 1
        if RJOY_DOWN in inp.held:
            dy += 1
        return dx, dy

    def was_pressed(self, inp: FrameInput, name: str) -> bool:
        return name in inp.pressed

    @staticmethod
    def quit_held(inp: FrameInput) -> bool:
        return "SELECT" in inp.held and "START" in inp.held
