"""Cámara con zoom entero y límites sobre área explorada."""

from __future__ import annotations

import math

from config import (
    CURSOR_MARGIN_TILES,
    CURSOR_TILES_PER_SEC_FAR,
    CURSOR_TILES_PER_SEC_NEAR,
    DEFAULT_ZOOM_LEVEL,
    PAN_TILES_PER_SEC_FAR,
    PAN_TILES_PER_SEC_NEAR,
    WORLD_SIZE,
    ZOOM_LEVELS,
)


def movement_rates(zoom: float) -> tuple[float, float]:
    """(cursor tiles/s, pan tiles/s) — más lento con zoom alto."""
    cursor = CURSOR_TILES_PER_SEC_FAR + (
        CURSOR_TILES_PER_SEC_NEAR - CURSOR_TILES_PER_SEC_FAR
    ) * zoom
    pan = PAN_TILES_PER_SEC_FAR + (PAN_TILES_PER_SEC_NEAR - PAN_TILES_PER_SEC_FAR) * zoom
    return cursor, pan


class Camera:
    def __init__(self, center_x: float, center_y: float) -> None:
        self.x = center_x
        self.y = center_y
        self.zoom_level = DEFAULT_ZOOM_LEVEL

    @property
    def zoom_t(self) -> float:
        if len(ZOOM_LEVELS) == 1:
            return 0.0
        return self.zoom_level / (len(ZOOM_LEVELS) - 1)

    @property
    def tile_px(self) -> int:
        return ZOOM_LEVELS[self.zoom_level]

    def update_zoom(self, zoom_in: bool, zoom_out: bool) -> None:
        if zoom_in:
            self.zoom_level = min(len(ZOOM_LEVELS) - 1, self.zoom_level + 1)
        if zoom_out:
            self.zoom_level = max(0, self.zoom_level - 1)

    def pan(self, dx: float, dy: float, bounds: tuple[int, int, int, int]) -> None:
        self.x += dx
        self.y += dy
        self.clamp(bounds)

    def clamp(self, bounds: tuple[int, int, int, int]) -> None:
        min_x, min_y, max_x, max_y = bounds
        self.x = max(min_x, min(max_x, self.x))
        self.y = max(min_y, min(max_y, self.y))

    def keep_tile_visible(
        self,
        tx: int,
        ty: int,
        map_x: int,
        map_y: int,
        map_w: int,
        map_h: int,
        bounds: tuple[int, int, int, int],
    ) -> None:
        """Ajusta la cámara para que el tile del cursor quede dentro del mapa visible."""
        px = self.tile_px
        margin = CURSOR_MARGIN_TILES * px
        sx = map_x + (tx - self.x) * px + map_w / 2
        sy = map_y + (ty - self.y) * px + map_h / 2

        left = map_x + margin
        right = map_x + map_w - margin - px
        top = map_y + margin
        bottom = map_y + map_h - margin - px

        if sx < left:
            self.x -= (left - sx) / px
        elif sx > right:
            self.x += (sx - right) / px
        if sy < top:
            self.y -= (top - sy) / px
        elif sy > bottom:
            self.y += (sy - bottom) / px

        self.clamp(bounds)

    def cursor_tile_bounds(
        self,
        map_x: int,
        map_y: int,
        map_w: int,
        map_h: int,
        cam_bounds: tuple[int, int, int, int],
        world_size: int = WORLD_SIZE,
    ) -> tuple[int, int, int, int]:
        """Tiles alcanzables sin salir del área explorada ni de la vista."""
        px = self.tile_px
        margin = CURSOR_MARGIN_TILES * px
        left = map_x + margin
        right = map_x + map_w - margin - px
        top = map_y + margin
        bottom = map_y + map_h - margin - px
        min_cx, min_cy, max_cx, max_cy = cam_bounds

        tx_min = min_cx + (left - map_x - map_w / 2) / px
        tx_max = max_cx + (right - map_x - map_w / 2) / px
        ty_min = min_cy + (top - map_y - map_h / 2) / px
        ty_max = max_cy + (bottom - map_y - map_h / 2) / px

        return (
            max(0, math.ceil(tx_min)),
            max(0, math.ceil(ty_min)),
            min(world_size - 1, math.floor(tx_max)),
            min(world_size - 1, math.floor(ty_max)),
        )

    def clamp_cursor(
        self,
        tx: int,
        ty: int,
        map_x: int,
        map_y: int,
        map_w: int,
        map_h: int,
        cam_bounds: tuple[int, int, int, int],
        world_size: int = WORLD_SIZE,
    ) -> tuple[int, int]:
        x0, y0, x1, y1 = self.cursor_tile_bounds(
            map_x, map_y, map_w, map_h, cam_bounds, world_size
        )
        if x0 <= x1:
            tx = max(x0, min(x1, tx))
        else:
            tx = x0
        if y0 <= y1:
            ty = max(y0, min(y1, ty))
        else:
            ty = y0
        return tx, ty

    def visible_tiles(self, map_w: int, map_h: int) -> tuple[int, int, int, int]:
        px = max(self.tile_px, 1.0)
        cols = int(map_w / px) + 3
        rows = int(map_h / px) + 3
        x0 = int(self.x - cols / 2)
        y0 = int(self.y - rows / 2)
        return (
            max(0, x0),
            max(0, y0),
            min(WORLD_SIZE, x0 + cols),
            min(WORLD_SIZE, y0 + rows),
        )

    def tile_to_screen(
        self, tx: int, ty: int, map_x: int, map_y: int, map_w: int, map_h: int
    ) -> tuple[float, float]:
        px = self.tile_px
        sx = map_x + (tx - self.x) * px + map_w / 2
        sy = map_y + (ty - self.y) * px + map_h / 2
        return sx, sy
