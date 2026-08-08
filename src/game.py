"""Bucle principal fase 1."""

from __future__ import annotations

import os
import time

import pygame

from camera import Camera
from config import (
    CAMERA_MARGIN,
    CAMERA_SPEED,
    CURSOR_SCROLL_EDGE,
    FPS,
    HABITAT_X,
    HABITAT_Y,
    JOY_CAMERA_SPEED,
    SCREEN_H,
    SCREEN_W,
)
from i18n import load, t
from input_state import Input
from ui import (
    MapLayer,
    draw_bottom_bar,
    draw_dev_debug,
    draw_map,
    draw_panel,
    draw_top_bar,
    map_rect,
)
from world import generate_world


def create_display() -> pygame.Surface:
    if os.environ.get("SOLITUDINE_HANDHELD") == "1":
        for flags in (pygame.SCALED | pygame.NOFRAME, pygame.SCALED, 0):
            try:
                return pygame.display.set_mode((SCREEN_W, SCREEN_H), flags)
            except pygame.error:
                pass
    return pygame.display.set_mode((SCREEN_W, SCREEN_H))


def run() -> int:
    dev_mode = (
        os.environ.get("SOLITUDINE_DEV") == "1"
        and os.environ.get("SOLITUDINE_HANDHELD") != "1"
    )

    if dev_mode:
        from dev_input import DEV_KEYMAP, setup_dev_display, setup_dev_env

        setup_dev_env()

    load("es")
    pygame.init()
    pygame.joystick.init()

    screen = create_display()
    if dev_mode:
        setup_dev_display()

    pygame.display.set_caption(t("game.title"))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 22)
    font_sm = pygame.font.Font(None, 18)

    t0 = time.perf_counter()
    world = generate_world()
    gen_ms = (time.perf_counter() - t0) * 1000.0

    camera = Camera(float(HABITAT_X), float(HABITAT_Y))
    inp = Input(dev_mode)
    inp.open_joysticks()

    cursor_x, cursor_y = HABITAT_X, HABITAT_Y
    select_x: int | None = None
    select_y: int | None = None
    layer = MapLayer.TERRAIN
    day = 1
    cam_bounds = world.camera_bounds(CAMERA_MARGIN)

    while True:
        frame_start = time.perf_counter()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 0
            inp.process_event(event)

        frame = inp.poll()

        if Input.quit_held(frame):
            pygame.quit()
            return 0

        if inp.was_pressed(frame, "L1"):
            camera.zoom_in()
        if inp.was_pressed(frame, "L2"):
            camera.zoom_out()
        if inp.was_pressed(frame, "X"):
            layer = MapLayer((layer.value + 1) % 3)

        cdx, cdy = inp.cursor_delta(frame)
        if cdx or cdy:
            cursor_x = max(0, min(world.size - 1, cursor_x + cdx))
            cursor_y = max(0, min(world.size - 1, cursor_y + cdy))
            _edge_scroll(camera, cursor_x, cursor_y, cdx, cdy, cam_bounds)

        pdx, pdy = inp.pan_delta(frame)
        if pdx or pdy:
            camera.pan(pdx * JOY_CAMERA_SPEED, pdy * JOY_CAMERA_SPEED, cam_bounds)

        if inp.was_pressed(frame, "A"):
            select_x, select_y = cursor_x, cursor_y

        camera.clamp(cam_bounds)

        screen.fill((0, 0, 0))
        draw_top_bar(screen, font, font_sm, day)
        tiles_drawn = draw_map(screen, world, camera, layer, cursor_x, cursor_y)
        draw_panel(screen, font, font_sm, world, select_x, select_y, layer)

        help_text = t("help.selected") if select_x is not None else t("help.default")
        if not dev_mode:
            draw_bottom_bar(screen, font_sm, help_text)
        else:
            draw_bottom_bar(screen, font_sm, t("help.default"))
            draw_dev_debug(
                screen,
                font_sm,
                fps=clock.get_fps(),
                frame_ms=(time.perf_counter() - frame_start) * 1000.0,
                tiles_drawn=tiles_drawn,
                gen_ms=gen_ms,
                held=frame.held,
                keymap=DEV_KEYMAP,
            )

        pygame.display.flip()
        clock.tick(FPS)


def _edge_scroll(
    camera: Camera,
    cx: int,
    cy: int,
    dx: int,
    dy: int,
    bounds: tuple[int, int, int, int],
) -> None:
    rect = map_rect()
    px = camera.tile_px
    sx, sy = camera.tile_to_screen(cx, cy, rect.x, rect.y, rect.w, rect.h)
    margin = CURSOR_SCROLL_EDGE * px
    step = CAMERA_SPEED * 0.05

    if dx < 0 and sx < rect.x + margin:
        camera.pan(-step, 0, bounds)
    elif dx > 0 and sx > rect.right - margin - px:
        camera.pan(step, 0, bounds)
    if dy < 0 and sy < rect.y + margin:
        camera.pan(0, -step, bounds)
    elif dy > 0 and sy > rect.bottom - margin - px:
        camera.pan(0, step, bounds)
