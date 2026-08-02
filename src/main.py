#!/usr/bin/env python3
"""Fase 0: depurador de mando directo (sin gptokeyb)."""

import os
import sys
from collections import deque

import pygame

from gamepad import DEADZONE, diff_actions, format_actions, read_actions

WIDTH = 640
HEIGHT = 480
FPS = 60
MAX_EVENTS = 12

BG = (16, 32, 16)
FG = (80, 255, 120)
DIM = (40, 120, 60)
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
    held_btns: dict[tuple[int, int], int] = {}
    prev_actions: dict[int, frozenset[str]] = {}

    if dev_mode:
        events_log.appendleft("dev: clic ventana, luego teclado")
    for i, joy in enumerate(joysticks):
        events_log.appendleft(f"joy{i}: {joy.get_name()}")

    dev_actions: frozenset[str] = frozenset()

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
                held_btns[(event.joy, event.button)] = event.button
            elif event.type == pygame.JOYBUTTONUP:
                held_btns.pop((event.joy, event.button), None)
            elif event.type == pygame.JOYDEVICEADDED:
                joy = pygame.joystick.Joystick(event.device_index)
                joy.init()
                joysticks.append(joy)
                events_log.appendleft(f"ADD   j{event.device_index} {joy.get_name()}")
            elif event.type == pygame.JOYDEVICEREMOVED:
                events_log.appendleft(f"REM   id {event.device_instance_id}")

        if dev_mode and dev_kb is not None:
            dev_actions, dev_events = dev_kb.tick()
            for entry in dev_events:
                events_log.appendleft(entry)
        else:
            for ji, joy in enumerate(joysticks):
                buttons = {b for (j, b) in held_btns if j == ji}
                curr = read_actions(joy, buttons)
                prev = prev_actions.get(ji, frozenset())
                for entry in diff_actions(ji, prev, curr):
                    events_log.appendleft(entry)
                prev_actions[ji] = curr

        screen.fill(BG)
        pygame.draw.rect(screen, FG, (0, 0, WIDTH, 4))
        y = 10

        def line(text: str, color=FG, small=True) -> None:
            nonlocal y
            f = font_sm if small else font
            screen.blit(f.render(text, True, color), (12, y))
            y += 17 if small else 22

        line("SOLITUDINE — Input Debug", FG, small=False)
        mode = "DEV teclado" if dev_mode else f"{len(joysticks)} dispositivo(s)"
        line(f"{mode}  |  deadzone: {DEADZONE}", DEV_COLOR if dev_mode else DIM)
        y += 4

        if dev_mode:
            line("[0] keyboard (dev)", DEV_COLOR)
            line(f"  {format_actions(dev_actions)}", FG if dev_actions else DIM)
            y += 2
        else:
            for ji, joy in enumerate(joysticks):
                buttons = {b for (j, b) in held_btns if j == ji}
                actions = read_actions(joy, buttons)
                line(f"[{ji}] {joy.get_name()}", DIM)
                line(f"  {format_actions(actions)}", FG if actions else DIM)
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
