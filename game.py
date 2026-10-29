"""Bucle principal — mapa, simulación, construcción y UI."""

from __future__ import annotations

import sys
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
from game_help import context_help
from game_input import handle_frame_input
from gamepad import LJOY_DOWN, LJOY_LEFT, LJOY_RIGHT, LJOY_UP
from i18n import load, t
from input_state import Input
from simulation import Simulation
import savegame
import ui_assets
from ui import (
    MapLayer,
    draw_bottom_bar,
    draw_build_menu_modal,
    draw_credits_modal,
    draw_easter_egg,
    draw_dev_debug,
    draw_game_over,
    draw_map,
    draw_panel,
    draw_pause_modal,
    draw_top_bar,
    map_rect,
    module_debug_lines,
)
from ui_input import input_policy
from ui_minimap import draw_minimap
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


def create_display(handheld: bool) -> pygame.Surface:
    if handheld:
        for flags in (pygame.SCALED | pygame.NOFRAME, pygame.SCALED, 0):
            try:
                return pygame.display.set_mode((SCREEN_W, SCREEN_H), flags)
            except pygame.error:
                pass
    return pygame.display.set_mode((SCREEN_W, SCREEN_H))


def run(dev: bool = False, handheld: bool = False) -> int:
    dev_mode = dev and not handheld

    if dev_mode:
        from dev_input import DEV_KEYMAP, setup_dev_display, setup_dev_env

        setup_dev_env()

    load("es")
    pygame.init()
    pygame.joystick.init()

    screen = create_display(handheld)
    if dev_mode:
        setup_dev_display()

    pygame.display.set_caption(t("game.title"))
    clock = pygame.time.Clock()
    ui_assets.load()
    font = ui_assets.font_lg()
    font_sm = ui_assets.font_sm()

    t0 = time.perf_counter()
    try:
        loaded = savegame.load_game()
    except Exception as exc:
        print(f"Guardado ignorado: {exc}", file=sys.stderr)
        loaded = None
    if loaded is None:
        world = generate_world()
        sim = Simulation()
    else:
        world, sim = loaded
    gen_ms = (time.perf_counter() - t0) * 1000.0

    camera = Camera(float(HABITAT_X), float(HABITAT_Y))
    inp = Input(dev_mode)
    inp.open_joysticks()

    cursor_x, cursor_y = HABITAT_X, HABITAT_Y
    select_x: int | None = None
    select_y: int | None = None
    layer = MapLayer.TERRAIN
    cam_bounds = world.camera_bounds(CAMERA_MARGIN)
    mrect = map_rect()
    cursor_acc_x = 0.0
    cursor_acc_y = 0.0
    minimap_on = True

    def save_now() -> None:
        if sim.game_over:
            return
        try:
            savegame.save_game(world, sim)
        except OSError as exc:
            print(f"No se pudo guardar: {exc}", file=sys.stderr)

    def reset_session() -> None:
        nonlocal world, sim, camera, cam_bounds, cursor_x, cursor_y
        nonlocal select_x, select_y, layer, cursor_acc_x, cursor_acc_y
        savegame.delete_save()
        world = generate_world()
        sim = Simulation()
        camera = Camera(float(HABITAT_X), float(HABITAT_Y))
        cam_bounds = world.camera_bounds(CAMERA_MARGIN)
        cursor_x, cursor_y = HABITAT_X, HABITAT_Y
        select_x, select_y = None, None
        layer = MapLayer.TERRAIN
        cursor_acc_x, cursor_acc_y = 0.0, 0.0

    while True:
        frame_start = time.perf_counter()
        dt = clock.get_time() / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_now()
                pygame.quit()
                return 0
            inp.process_event(event)

        frame = inp.poll()

        if "R2" in frame.pressed:
            minimap_on = not minimap_on

        if Input.quit_held(frame):
            save_now()
            pygame.quit()
            return 0

        build = sim.build
        policy = input_policy(
            build,
            game_over=sim.game_over,
            user_paused=sim.user_paused,
            tech_open=sim.research.open,
        )
        sim.paused = policy.pause_time

        was_paused = sim.user_paused

        input_result = handle_frame_input(
            frame,
            inp,
            sim,
            world,
            layer=layer,
            cursor_x=cursor_x,
            cursor_y=cursor_y,
            select_x=select_x,
            select_y=select_y,
        )
        if input_result.reset_session:
            reset_session()
            continue
        layer = input_result.layer
        select_x, select_y = input_result.select_x, input_result.select_y
        pause_modal = not sim.game_over and sim.user_paused

        if not was_paused and sim.user_paused:
            save_now()

        previous_day = sim.day
        sim.update(dt, world)
        if sim.day != previous_day:
            save_now()

        if not policy.block_camera_pan:
            camera.update_zoom("L1" in frame.pressed, "L2" in frame.pressed)
        cursor_rate, pan_rate = movement_rates(camera.zoom_t)

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
        draw_minimap(
            screen,
            world,
            camera,
            cursor_x=cursor_x,
            cursor_y=cursor_y,
            visible=minimap_on,
        )
        draw_top_bar(screen, font, font_sm, sim, world)
        draw_panel(
            screen, font, font_sm, world, sim, select_x, select_y, layer,
            cursor_x=cursor_x, cursor_y=cursor_y,
        )

        help_text = context_help(sim, build, select_x=select_x)

        draw_bottom_bar(screen, font_sm, help_text)
        if dev_mode:
            debug_lines = None
            if select_x is not None and select_y is not None:
                selected_mod = world.module_at(select_x, select_y)
                if selected_mod is not None:
                    debug_lines = module_debug_lines(sim, world, selected_mod)
            draw_dev_debug(
                screen,
                font_sm,
                fps=clock.get_fps(),
                frame_ms=(time.perf_counter() - frame_start) * 1000.0,
                tiles_drawn=tiles_drawn,
                gen_ms=gen_ms,
                held=frame.held,
                keymap=DEV_KEYMAP,
                zoom_px=camera.tile_px,
                debug_lines=debug_lines,
            )

        if sim.game_over:
            draw_game_over(screen, font, font_sm, sim)
        elif sim.research.open:
            draw_tech_screen(screen, font, font_sm, sim, world)
        elif pause_modal:
            if sim.credits_open:
                draw_credits_modal(screen, font, font_sm, sim)
            else:
                draw_pause_modal(screen, font, font_sm, sim)
        elif build.mode == BuildMode.MENU:
            draw_build_menu_modal(screen, font, font_sm, sim, world)

        if sim.easter_egg_open:
            draw_easter_egg(screen)

        pygame.display.flip()
        clock.tick(FPS)
