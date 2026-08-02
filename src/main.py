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
DEV_COLOR = (120, 180, 255)


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
    dev_mode = (
        os.environ.get("SOLITUDINE_DEV") == "1"
        and os.environ.get("SOLITUDINE_HANDHELD") != "1"
    )
    dev_kb = None
    if dev_mode:
        from dev_input import DevKeyboard, HELP, setup_dev_display, setup_dev_env

        setup_dev_env()

    pygame.init()
    pygame.joystick.init()

    screen = create_display()
    if dev_mode:
        setup_dev_display()
        dev_kb = DevKeyboard()

    title = "SOLITUDINE — Input Debug"
    if dev_mode:
        title += " [DEV]"
    pygame.display.set_caption(title)
    clock = pygame.time.Clock()
    font = load_font(22)
    font_sm = load_font(16)

    joysticks = open_joysticks() if not dev_mode else []
    events_log: deque[str] = deque(maxlen=MAX_EVENTS)
    held: dict[tuple[int, int], int] = {}

    if dev_mode:
        events_log.appendleft("dev: clic ventana, luego teclado")
    for i, joy in enumerate(joysticks):
        events_log.appendleft(f"joy{i}: {joy.get_name()}")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 0
            if dev_mode and dev_kb is not None:
                if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                    for entry in dev_kb.on_event(event):
                        events_log.appendleft(entry)
                continue
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

        if dev_mode and dev_kb is not None:
            dev_state, dev_events = dev_kb.tick()
            held = {(0, btn): btn for btn in dev_state.held}
            for entry in dev_events:
                events_log.appendleft(entry)
        else:
            dev_state = None

        screen.fill(BG)
        pygame.draw.rect(screen, FG, (0, 0, WIDTH, 4))
        y = 10

        def line(text: str, color=FG, small=True) -> None:
            nonlocal y
            f = font_sm if small else font
            screen.blit(f.render(text, True, color), (12, y))
            y += 17 if small else 22

        line("SOLITUDINE — Mando directo", FG, small=False)
        mode = "DEV teclado" if dev_mode else f"{len(joysticks)} dispositivo(s)"
        line(f"{mode}  |  deadzone: {DEADZONE}", DEV_COLOR if dev_mode else DIM)
        y += 4

        if dev_mode and dev_state is not None:
            line("[0] keyboard (dev)", DEV_COLOR)
            names = [button_name(b).split(" (")[0] for b in sorted(dev_state.held)]
            line(f"  btns: {', '.join(names) if names else '-'}", FG if names else DIM)
            parts = [
                f"{ax}:{val:+.2f}"
                for ax, val in sorted(dev_state.axes.items())
                if axis_active(val)
            ]
            line(
                f"  ejes: {' '.join(parts) if parts else '(WASD / flechas)'}",
                ACTIVE if parts else DIM,
            )
            y += 2
        else:
            for ji, joy in enumerate(joysticks):
                line(f"[{ji}] {joy.get_name()}", DIM)
                names = [
                    button_name(b).split(" (")[0]
                    for (j, b) in sorted(held)
                    if j == ji
                ]
                line(f"  btns: {', '.join(names) if names else '-'}", FG if names else DIM)
                parts = [
                    f"{ax}:{joy.get_axis(ax):+.2f}"
                    for ax in range(joy.get_numaxes())
                    if axis_active(joy.get_axis(ax))
                ]
                line(
                    f"  ejes: {' '.join(parts) if parts else '(mueve sticks)'}",
                    ACTIVE if parts else DIM,
                )
                y += 2

        y += 4
        line("Eventos:", DIM)
        for entry in events_log:
            line(f"  {entry}", FG)

        if dev_mode:
            screen.blit(font_sm.render(HELP, True, DEV_COLOR), (12, HEIGHT - 28))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    sys.exit(main())
