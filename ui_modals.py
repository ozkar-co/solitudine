"""Modales centrados sobre el área del mapa."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from ui_theme import COL_BORDER, COL_PANEL, map_rect

MODAL_PAD_X = 16
MODAL_PAD_Y = 12
MODAL_DIM_ALPHA = 100


@dataclass(frozen=True)
class ModalLine:
    text: str
    color: tuple[int, int, int]
    large: bool = False


def draw_map_modal(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
    lines: list[ModalLine],
    *,
    dim_map: bool = False,
    min_width: int = 0,
    fixed_height: int = 0,
) -> pygame.Rect:
    """Dibuja un recuadro centrado en el mapa. Una sola implementación para todos los modales."""
    if not lines:
        return pygame.Rect(0, 0, 0, 0)

    mrect = map_rect()
    if dim_map:
        overlay = pygame.Surface((mrect.w, mrect.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, MODAL_DIM_ALPHA))
        surf.blit(overlay, (mrect.x, mrect.y))

    pad_x, pad_y = MODAL_PAD_X, MODAL_PAD_Y
    rendered: list[tuple[pygame.Surface, bool]] = []
    w = pad_x * 2
    h = pad_y * 2
    for line in lines:
        fnt = font if line.large else font_sm
        s = fnt.render(line.text, False, line.color)
        rendered.append((s, line.large))
        w = max(w, s.get_width() + pad_x * 2)
        h += s.get_height() + (4 if line.large else 2)

    w = max(w, min_width)
    if fixed_height > 0:
        h = fixed_height

    box = pygame.Rect(0, 0, w, h)
    box.center = (mrect.centerx, mrect.centery)
    pygame.draw.rect(surf, COL_PANEL, box)
    pygame.draw.rect(surf, COL_BORDER, box, 2)

    y = box.y + pad_y
    for s, large in rendered:
        surf.blit(s, (box.centerx - s.get_width() // 2, y))
        y += s.get_height() + (4 if large else 2)

    return box
