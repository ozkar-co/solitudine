#!/usr/bin/env python3
"""Fase 0: depurador de mando directo (sin gptokeyb)."""

import os
import sys
from collections import deque

import pygame

from gamepad import DEADZONE, axis_active, button_name

WIDTH = 640
HEIGHT = 480
FPS = 60
MAX_EVENTS = 12

BG = (16, 32, 16)
FG = (80, 255, 120)
DIM = (40, 120, 60)
ACTIVE = (255, 200, 80)


def load_font(size: int) -> pygame.font.Font:
    return pygame.font.Font(None, size)


def create_display() -> pygame.Surface:
    if os.environ.get("SOLITUDINE_HANDHELD") == "1":
        for flags in (pygame.SCALED | pygame.NOFRAME, pygame.SCALED, 0):
            try:
                return pygame.display.set_mode((WIDTH, HEIGHT), flags)
            except pygame.error:
                pass
    return pygame.display.set_mode((WIDTH, HEIGHT))


def open_joysticks() -> list[pygame.joystick.Joystick]:
    sticks: list[pygame.joystick.Joystick] = []
    for i in range(pygame.joystick.get_count()):
        joy = pygame.joystick.Joystick(i)
        joy.init()
        sticks.append(joy)
    return sticks


def main() -> int:
    pygame.init()
    pygame.joystick.init()

    screen = create_display()
    pygame.display.set_caption("SOLITUDINE — Input Debug")
    clock = pygame.time.Clock()
    font = load_font(22)
    font_sm = load_font(16)

    joysticks = open_joysticks()
    events_log: deque[str] = deque(maxlen=MAX_EVENTS)
    held: dict[tuple[int, int], int] = {}

    for i, joy in enumerate(joysticks):
        events_log.appendleft(f"joy{i}: {joy.get_name()}")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 0
            if event.type == pygame.JOYBUTTONDOWN:
                held[(event.joy, event.button)] = event.button
                events_log.appendleft(f"DOWN  j{event.joy} {button_name(event.button)}")
            elif event.type == pygame.JOYBUTTONUP:
                held.pop((event.joy, event.button), None)
                events_log.appendleft(f"UP    j{event.joy} {button_name(event.button)}")
            elif event.type == pygame.JOYAXISMOTION:
                if axis_active(event.value):
                    events_log.appendleft(
                        f"AXIS  j{event.joy} ax{event.axis} {event.value:+.2f}"
                    )
            elif event.type == pygame.JOYDEVICEADDED:
                joy = pygame.joystick.Joystick(event.device_index)
                joy.init()
                joysticks.append(joy)
                events_log.appendleft(f"ADD   j{event.device_index} {joy.get_name()}")
            elif event.type == pygame.JOYDEVICEREMOVED:
                events_log.appendleft(f"REM   id {event.device_instance_id}")

        screen.fill(BG)
        pygame.draw.rect(screen, FG, (0, 0, WIDTH, 4))
        y = 10

        def line(text: str, color=FG, small=True) -> None:
            nonlocal y
            f = font_sm if small else font
            screen.blit(f.render(text, True, color), (12, y))
            y += 17 if small else 22

        line("SOLITUDINE — Mando directo", FG, small=False)
        line(f"Dispositivos: {len(joysticks)}  |  deadzone: {DEADZONE}", DIM)
        y += 4

        for ji, joy in enumerate(joysticks):
            line(f"[{ji}] {joy.get_name()}", DIM)
            names = [
                button_name(b).split(" (")[0]
                for (j, b) in sorted(held)
                if j == ji
            ]
            line(f"  btns: {', '.join(names) if names else '-'}", FG if names else DIM)

            parts: list[str] = []
            for ax in range(joy.get_numaxes()):
                v = joy.get_axis(ax)
                if axis_active(v):
                    parts.append(f"{ax}:{v:+.2f}")
            line(
                f"  ejes: {' '.join(parts) if parts else '(mueve sticks)'}",
                ACTIVE if parts else DIM,
            )
            y += 2

        y += 4
        line("Eventos:", DIM)
        for entry in events_log:
            line(f"  {entry}", FG)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    sys.exit(main())
