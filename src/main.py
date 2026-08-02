#!/usr/bin/env python3
"""Fase 0: depurador de entrada para PortMaster / R36S."""

import os
import sys
from collections import deque

import pygame

WIDTH = 640
HEIGHT = 480
FPS = 60
MAX_EVENTS = 14

BG = (16, 32, 16)
FG = (80, 255, 120)
DIM = (40, 120, 60)
WARN = (255, 200, 80)


def key_label(key: int) -> str:
    name = pygame.key.name(key)
    if name:
        return f"{name.upper()} ({key})"
    return f"KEY_{key}"


def load_font(size: int) -> pygame.font.Font:
    # Font(None) usa la fuente incluida en pygame (sin fc-list del sistema)
    return pygame.font.Font(None, size)


def create_display() -> pygame.Surface:
    handheld = os.environ.get("SOLITUDINE_HANDHELD") == "1"
    if handheld:
        for flags in (pygame.SCALED | pygame.NOFRAME, pygame.SCALED, 0):
            try:
                screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
                print(f"display ok: {screen.get_size()} flags={flags}")
                return screen
            except pygame.error as exc:
                print(f"display fallo flags={flags}: {exc}")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    print(f"display ok: {screen.get_size()} (ventana)")
    return screen


def main() -> int:
    print("iniciando solitudine fase 0")
    print(f"SDL_VIDEODRIVER={os.environ.get('SDL_VIDEODRIVER', '(auto)')}")

    pygame.init()
    pygame.joystick.init()

    screen = create_display()
    pygame.display.set_caption("SOLITUDINE — Input Debug")
    clock = pygame.time.Clock()

    font = load_font(24)
    font_sm = load_font(18)

    events_log: deque[str] = deque(maxlen=MAX_EVENTS)
    held_keys: set[int] = set()
    held_buttons: dict[tuple[int, int], str] = {}
    hat_state: dict[tuple[int, int], tuple[int, int]] = {}

    joysticks: list[pygame.joystick.Joystick] = []
    for i in range(pygame.joystick.get_count()):
        joy = pygame.joystick.Joystick(i)
        joy.init()
        joysticks.append(joy)
        events_log.appendleft(f"JOY {i}: {joy.get_name()}")

    running = True
    frames = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                else:
                    held_keys.add(event.key)
                    events_log.appendleft(f"KEY DOWN  {key_label(event.key)}")
            elif event.type == pygame.KEYUP:
                held_keys.discard(event.key)
                events_log.appendleft(f"KEY UP    {key_label(event.key)}")
            elif event.type == pygame.JOYBUTTONDOWN:
                held_buttons[(event.joy, event.button)] = "DOWN"
                events_log.appendleft(
                    f"BTN DOWN  joy{event.joy} btn{event.button}"
                )
            elif event.type == pygame.JOYBUTTONUP:
                held_buttons.pop((event.joy, event.button), None)
                events_log.appendleft(
                    f"BTN UP    joy{event.joy} btn{event.button}"
                )
            elif event.type == pygame.JOYHATMOTION:
                hat_state[(event.joy, event.hat)] = event.value
                x, y = event.value
                if x or y:
                    events_log.appendleft(
                        f"HAT       joy{event.joy} ({x:+d},{y:+d})"
                    )
            elif event.type == pygame.JOYDEVICEADDED:
                joy = pygame.joystick.Joystick(event.device_index)
                joy.init()
                joysticks.append(joy)
                events_log.appendleft(f"JOY ADD   {joy.get_name()}")
            elif event.type == pygame.JOYDEVICEREMOVED:
                events_log.appendleft(f"JOY REM   id {event.device_instance_id}")

        screen.fill(BG)
        pygame.draw.rect(screen, FG, (0, 0, WIDTH, 4))
        y = 12

        def line(text: str, color=FG, small=False) -> None:
            nonlocal y
            f = font_sm if small else font
            screen.blit(f.render(text, True, color), (16, y))
            y += 22 if not small else 18

        line("SOLITUDINE — Input Debug (fase 0)", FG)
        line("Teclado + mando -> eventos en pantalla", DIM, small=True)
        y += 6

        line(f"Joysticks: {len(joysticks)}", DIM, small=True)
        for i, joy in enumerate(joysticks):
            line(f"  [{i}] {joy.get_name()}", DIM, small=True)
        y += 8

        line("Teclas pulsadas:")
        if held_keys:
            labels = ", ".join(sorted(pygame.key.name(k).upper() for k in held_keys))
            line(f"  {labels}", FG, small=True)
        else:
            line("  (ninguna)", DIM, small=True)
        y += 8

        line("Botones mando:")
        if held_buttons:
            for (joy, btn), _ in sorted(held_buttons.items()):
                line(f"  joy{joy} btn{btn}", FG, small=True)
        else:
            line("  (ninguno)", DIM, small=True)
        y += 8

        active_hats = [(j, h, v) for (j, h), v in hat_state.items() if v != (0, 0)]
        if active_hats:
            line("Cruceta (hat):")
            for j, h, (hx, hy) in active_hats:
                line(f"  joy{j} hat{h} ({hx:+d},{hy:+d})", FG, small=True)
            y += 4

        line("Ultimos eventos:")
        if events_log:
            for entry in events_log:
                line(f"  {entry}", FG, small=True)
        else:
            line("  (esperando entrada...)", DIM, small=True)

        footer = "Select=ESC salir  |  gptokeyb -> teclado"
        screen.blit(font_sm.render(footer, True, WARN), (16, HEIGHT - 28))

        pygame.display.flip()
        clock.tick(FPS)

        frames += 1
        if frames == 1:
            print("primer frame dibujado")
        elif frames % 300 == 0:
            print(f"heartbeat: {frames} frames")

    print("salida normal")
    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
