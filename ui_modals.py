"""Modales centrados sobre el área del mapa."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

import ui_assets
from ui_theme import COL_BORDER, COL_DIM, COL_PANEL, COL_TEXT, map_rect

MODAL_PAD_X = 16
MODAL_PAD_Y = 12
MODAL_DIM_ALPHA = 100
MODAL_HEIGHT = 256
MODAL_FOOTER_GAP = 8
MODAL_ITEM_GAP = 12
MODAL_ICON_GAP = 4

ModalColor = tuple[int, int, int]
ModalItem = tuple[str, str, ModalColor]
ModalSegment = tuple[str, ModalColor]


@dataclass(frozen=True)
class ModalLine:
    text: str = ""
    color: ModalColor = COL_TEXT
    large: bool = False
    icon: str | None = None
    items: tuple[ModalItem, ...] = ()
    segments: tuple[ModalSegment, ...] = ()


def _render_items(items: tuple[ModalItem, ...], font_sm: pygame.font.Font) -> pygame.Surface:
    pieces: list[pygame.Surface] = []
    for icon_name, text, color in items:
        icon = ui_assets.icon(icon_name)
        label = font_sm.render(text, False, color)
        h = max(icon.get_height(), label.get_height())
        piece = pygame.Surface((icon.get_width() + MODAL_ICON_GAP + label.get_width(), h), pygame.SRCALPHA)
        piece.blit(icon, (0, (h - icon.get_height()) // 2))
        piece.blit(label, (icon.get_width() + MODAL_ICON_GAP, (h - label.get_height()) // 2))
        pieces.append(piece)

    width = sum(piece.get_width() for piece in pieces) + MODAL_ITEM_GAP * (len(pieces) - 1)
    height = max(piece.get_height() for piece in pieces)
    row = pygame.Surface((width, height), pygame.SRCALPHA)
    x = 0
    for piece in pieces:
        row.blit(piece, (x, (height - piece.get_height()) // 2))
        x += piece.get_width() + MODAL_ITEM_GAP
    return row


def _render_segments(segments: tuple[ModalSegment, ...], font_sm: pygame.font.Font) -> pygame.Surface:
    pieces = [font_sm.render(text, False, color) for text, color in segments]
    width = sum(piece.get_width() for piece in pieces)
    height = max(piece.get_height() for piece in pieces)
    row = pygame.Surface((width, height), pygame.SRCALPHA)
    x = 0
    for piece in pieces:
        row.blit(piece, (x, (height - piece.get_height()) // 2))
        x += piece.get_width()
    return row


def _render_line(line: ModalLine, font: pygame.font.Font, font_sm: pygame.font.Font) -> pygame.Surface:
    if line.items:
        return _render_items(line.items, font_sm)
    if line.segments:
        return _render_segments(line.segments, font_sm)

    fnt = font if line.large else font_sm
    label = fnt.render(line.text, False, line.color)
    if line.icon is None:
        return label

    icon = ui_assets.icon(line.icon)
    h = max(icon.get_height(), label.get_height())
    row = pygame.Surface((icon.get_width() + MODAL_ICON_GAP + label.get_width(), h), pygame.SRCALPHA)
    row.blit(icon, (0, (h - icon.get_height()) // 2))
    row.blit(label, (icon.get_width() + MODAL_ICON_GAP, (h - label.get_height()) // 2))
    return row


def _line_step(line: ModalLine, surface: pygame.Surface) -> int:
    return surface.get_height() + (4 if line.large else 2)


def draw_map_modal(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
    lines: list[ModalLine],
    *,
    dim_map: bool = False,
    min_width: int = 0,
    fixed_height: int = 0,
    footer: list[ModalLine] | None = None,
) -> pygame.Rect:
    """Dibuja un recuadro centrado en el mapa. Una sola implementación para todos los modales."""
    footer = footer or []
    if not lines and not footer:
        return pygame.Rect(0, 0, 0, 0)

    mrect = map_rect()
    if dim_map:
        overlay = pygame.Surface((mrect.w, mrect.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, MODAL_DIM_ALPHA))
        surf.blit(overlay, (mrect.x, mrect.y))

    pad_x, pad_y = MODAL_PAD_X, MODAL_PAD_Y
    rendered = [(line, _render_line(line, font, font_sm)) for line in lines]
    footer_rendered = [(line, _render_line(line, font, font_sm)) for line in footer]

    w = pad_x * 2
    h = pad_y * 2
    for line, s in rendered:
        w = max(w, s.get_width() + pad_x * 2)
        h += _line_step(line, s)
    for line, s in footer_rendered:
        w = max(w, s.get_width() + pad_x * 2)

    footer_h = sum(_line_step(line, s) for line, s in footer_rendered)
    if footer_rendered:
        footer_h += MODAL_FOOTER_GAP

    w = max(w, min_width)
    if fixed_height > 0:
        h = fixed_height
    else:
        h += footer_h

    box = pygame.Rect(0, 0, w, h)
    box.center = (mrect.centerx, mrect.centery)
    pygame.draw.rect(surf, COL_PANEL, box)
    pygame.draw.rect(surf, COL_BORDER, box, 2)

    y = box.y + pad_y
    for line, s in rendered:
        surf.blit(s, (box.centerx - s.get_width() // 2, y))
        y += _line_step(line, s)

    if footer_rendered:
        footer_top = box.bottom - pad_y - footer_h + MODAL_FOOTER_GAP
        pygame.draw.line(
            surf,
            COL_DIM,
            (box.x + pad_x, footer_top - MODAL_FOOTER_GAP),
            (box.right - pad_x, footer_top - MODAL_FOOTER_GAP),
        )
        y = footer_top
        for line, s in footer_rendered:
            surf.blit(s, (box.centerx - s.get_width() // 2, y))
            y += _line_step(line, s)

    return box
