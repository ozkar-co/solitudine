"""Bucle principal — mapa, simulación, construcción y UI."""

from __future__ import annotations

import os
import time

import pygame

from camera import Camera, movement_rates
from config import (
    CAMERA_MARGIN,
    FPS,
    HABITAT_X,
    HABITAT_Y,
    SCREEN_H,
    SCREEN_W,
)
from construction import BuildMode
from gamepad import LJOY_DOWN, LJOY_LEFT, LJOY_RIGHT, LJOY_UP
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
from ui_input import input_policy
from simulation import Simulation
from world import generate_world


def _axis_active(held: frozenset[str], pressed: frozenset[str], *names: str) -> tuple[bool, bool]:
    h = any(n in held for n in names)
    p = any(n in pressed for n in names)
    return h, p


def _step_cursor_axis(
    value: int,
    acc: float,
    neg_held: bool,
    pos_held: bool,
    neg_pressed: bool,
    pos_pressed: bool,
    rate: float,
    dt: float,
) -> tuple[int, float]:
    if neg_pressed:
        value -= 1
        acc = 0.0
    elif pos_pressed:
        value += 1
        acc = 0.0
    elif neg_held:
        acc -= rate * dt
        while acc <= -1.0:
            value -= 1
            acc += 1.0
    elif pos_held:
        acc += rate * dt
        while acc >= 1.0:
            value += 1
            acc -= 1.0
    else:
        acc = 0.0
    return value, acc


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
    sim = Simulation()
    cam_bounds = world.camera_bounds(CAMERA_MARGIN)
    mrect = map_rect()
    cursor_acc_x = 0.0
    cursor_acc_y = 0.0

    while True:
        frame_start = time.perf_counter()
        dt = clock.get_time() / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 0
            inp.process_event(event)

        frame = inp.poll()

        if Input.quit_held(frame):
            pygame.quit()
            return 0

        build = sim.build
        policy = input_policy(build)
        sim.paused = policy.pause_time

        if inp.was_pressed(frame, "B"):
            if build.mode == BuildMode.NONE:
                build.enter_menu()
            elif build.mode == BuildMode.MENU:
                build.exit_menu()
            elif build.mode == BuildMode.PLACE:
                build.back_to_menu()

        if build.mode == BuildMode.MENU:
            if inp.was_pressed(frame, "DPAD_UP") or inp.was_pressed(frame, LJOY_UP):
                build.menu_up()
            if inp.was_pressed(frame, "DPAD_DOWN") or inp.was_pressed(frame, LJOY_DOWN):
                build.menu_down()
            if inp.was_pressed(frame, "A"):
                build.enter_place()

        elif build.mode == BuildMode.PLACE:
            if inp.was_pressed(frame, "A"):
                build.try_place(world, sim.stock, cursor_x, cursor_y)

        else:
            if inp.was_pressed(frame, "X"):
                layer = MapLayer((layer.value + 1) % 3)
            if inp.was_pressed(frame, "A"):
                select_x, select_y = cursor_x, cursor_y

        sim.update(dt, world)

        camera.update_zoom(dt, "L1" in frame.held, "L2" in frame.held)
        cursor_rate, pan_rate = movement_rates(camera.zoom)

        if not policy.block_cursor:
            lx_h, lx_p = _axis_active(frame.held, frame.pressed, LJOY_LEFT, "DPAD_LEFT")
            rx_h, rx_p = _axis_active(frame.held, frame.pressed, LJOY_RIGHT, "DPAD_RIGHT")
            uy_h, uy_p = _axis_active(frame.held, frame.pressed, LJOY_UP, "DPAD_UP")
            dy_h, dy_p = _axis_active(frame.held, frame.pressed, LJOY_DOWN, "DPAD_DOWN")

            cursor_x, cursor_acc_x = _step_cursor_axis(
                cursor_x, cursor_acc_x, lx_h, rx_h, lx_p, rx_p, cursor_rate, dt
            )
            cursor_y, cursor_acc_y = _step_cursor_axis(
                cursor_y, cursor_acc_y, uy_h, dy_h, uy_p, dy_p, cursor_rate, dt
            )
            cursor_x, cursor_y = camera.clamp_cursor(
                cursor_x,
                cursor_y,
                mrect.x,
                mrect.y,
                mrect.w,
                mrect.h,
                cam_bounds,
                world.size,
            )

        if not policy.block_camera_pan:
            pdx, pdy = inp.pan_delta(frame)
            if pdx or pdy:
                camera.pan(pdx * pan_rate * dt, pdy * pan_rate * dt, cam_bounds)

        camera.keep_tile_visible(
            cursor_x,
            cursor_y,
            mrect.x,
            mrect.y,
            mrect.w,
            mrect.h,
            cam_bounds,
        )

        screen.fill((0, 0, 0))
        tiles_drawn = draw_map(screen, world, sim, camera, layer, cursor_x, cursor_y)
        draw_top_bar(screen, font, font_sm, sim)
        draw_panel(screen, font, font_sm, world, sim, select_x, select_y, layer)

        if build.mode == BuildMode.MENU:
            help_text = t("help.build_menu")
        elif build.mode == BuildMode.PLACE:
            help_text = t("help.build_place")
        elif select_x is not None:
            help_text = t("help.selected")
        else:
            help_text = t("help.default")

        if not dev_mode:
            draw_bottom_bar(screen, font_sm, help_text)
        else:
            draw_bottom_bar(screen, font_sm, help_text)
            draw_dev_debug(
                screen,
                font_sm,
                fps=clock.get_fps(),
                frame_ms=(time.perf_counter() - frame_start) * 1000.0,
                tiles_drawn=tiles_drawn,
                gen_ms=gen_ms,
                held=frame.held,
                keymap=DEV_KEYMAP,
                zoom_pct=camera.zoom * 100.0,
            )

        pygame.display.flip()
        clock.tick(FPS)
