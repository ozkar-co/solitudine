"""Cámara con zoom y límites sobre área explorada."""

from __future__ import annotations

from config import CAMERA_MARGIN, TILE_PX_LEVELS, WORLD_SIZE


class Camera:
    def __init__(self, center_x: float, center_y: float) -> None:
        self.x = center_x
        self.y = center_y
        self.zoom_index = 1

    @property
    def tile_px(self) -> int:
        return TILE_PX_LEVELS[self.zoom_index]

    def zoom_in(self) -> None:
        if self.zoom_index < len(TILE_PX_LEVELS) - 1:
            self.zoom_index += 1

    def zoom_out(self) -> None:
        if self.zoom_index > 0:
            self.zoom_index -= 1

    def pan(self, dx: float, dy: float, bounds: tuple[int, int, int, int]) -> None:
        self.x += dx
        self.y += dy
        self.clamp(bounds)

    def clamp(self, bounds: tuple[int, int, int, int]) -> None:
        min_x, min_y, max_x, max_y = bounds
        self.x = max(min_x, min(max_x, self.x))
        self.y = max(min_y, min(max_y, self.y))

    def visible_tiles(self, map_w: int, map_h: int) -> tuple[int, int, int, int]:
        """Rango aproximado de tiles visibles (x0, y0, x1, y1)."""
        px = self.tile_px
        cols = map_w // px + 2
        rows = map_h // px + 2
        x0 = int(self.x - cols / 2)
        y0 = int(self.y - rows / 2)
        x1 = x0 + cols
        y1 = y0 + rows
        return (
            max(0, x0),
            max(0, y0),
            min(WORLD_SIZE, x1),
            min(WORLD_SIZE, y1),
        )

    def tile_to_screen(
        self, tx: int, ty: int, map_x: int, map_y: int, map_w: int, map_h: int
    ) -> tuple[int, int]:
        px = self.tile_px
        sx = map_x + (tx - self.x) * px + map_w // 2
        sy = map_y + (ty - self.y) * px + map_h // 2
        return int(sx), int(sy)

    def screen_to_tile(
        self, sx: int, sy: int, map_x: int, map_y: int, map_w: int, map_h: int
    ) -> tuple[int, int]:
        px = self.tile_px
        tx = self.x + (sx - map_x - map_w // 2) / px
        ty = self.y + (sy - map_y - map_h // 2) / px
        return int(tx), int(ty)
