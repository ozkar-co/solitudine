"""Modales centrados sobre el área del mapa."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

import ui_assets
from ui_theme import COL_BORDER, COL_DIM, COL_PANEL, COL_TEXT, COL_WARN, map_rect

MODAL_PAD_X = 16
MODAL_PAD_Y = 12
MODAL_MARGIN = 8
MODAL_DIM_ALPHA = 100
MODAL_COLUMN_GAP = 24
BUILD_CARD_HEIGHT = 58
BUILD_CARD_GAP = 6
BUILD_CARD_ICON = 32
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
    item_gap: int = MODAL_ITEM_GAP
    segments: tuple[ModalSegment, ...] = ()


def _render_items(
    items: tuple[ModalItem, ...],
    font_sm: pygame.font.Font,
    gap: int,
) -> pygame.Surface:
    pieces: list[pygame.Surface] = []
    for icon_name, text, color in items:
        label = font_sm.render(text, False, color)
        if not icon_name:
            pieces.append(label)
            continue
        icon = ui_assets.icon(icon_name)
        h = max(icon.get_height(), label.get_height())
        piece = pygame.Surface((icon.get_width() + MODAL_ICON_GAP + label.get_width(), h), pygame.SRCALPHA)
        piece.blit(icon, (0, (h - icon.get_height()) // 2))
        piece.blit(label, (icon.get_width() + MODAL_ICON_GAP, (h - label.get_height()) // 2))
        pieces.append(piece)

    width = sum(piece.get_width() for piece in pieces) + gap * (len(pieces) - 1)
    height = max(piece.get_height() for piece in pieces)
    row = pygame.Surface((width, height), pygame.SRCALPHA)
    x = 0
    for piece in pieces:
        row.blit(piece, (x, (height - piece.get_height()) // 2))
        x += piece.get_width() + gap
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


def render_items(
    items: tuple[ModalItem, ...],
    font_sm: pygame.font.Font,
    gap: int = MODAL_ITEM_GAP,
) -> pygame.Surface:
    return _render_items(items, font_sm, gap)


def render_segments(
    segments: tuple[ModalSegment, ...],
    font_sm: pygame.font.Font,
) -> pygame.Surface:
    return _render_segments(segments, font_sm)


def _render_line(line: ModalLine, font: pygame.font.Font, font_sm: pygame.font.Font) -> pygame.Surface:
    if line.items:
        return _render_items(line.items, font_sm, line.item_gap)
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


@dataclass(frozen=True)
class ModalColumn:
    header: str = ""
    lines: tuple[ModalLine, ...] = ()
    align: str = "center"


@dataclass(frozen=True)
class ModalSpec:
    title: str = ""
    subtitle: str = ""
    columns: tuple[ModalColumn, ...] = ()
    help_text: str = ""
    wide: bool = True
    visible_lines: int = 0
    min_height: int = 0
    fill_height: bool = False
    min_width: int = 0
    dim_map: bool = True
    title_color: ModalColor = COL_TEXT


@dataclass(frozen=True)
class ModalResult:
    box: pygame.Rect
    content: pygame.Rect
    max_scroll: int


def draw_scrollbar(
    surf: pygame.Surface,
    track_x: int,
    track_top: int,
    track_h: int,
    visible: int,
    total: int,
    scroll: float,
) -> None:
    """Barra de scroll compartida por modales de líneas y de tarjetas."""
    if total <= visible or track_h <= 0:
        return
    visible = max(1, visible)
    max_scroll = max(1, total - visible)
    scroll = max(0.0, min(float(scroll), float(max_scroll)))
    track_h = max(1, track_h)
    thumb_h = max(10, int(track_h * visible / total))
    thumb_y = track_top + int((track_h - thumb_h) * scroll / max_scroll)
    pygame.draw.rect(surf, COL_DIM, (track_x, track_top, 2, track_h))
    pygame.draw.rect(surf, COL_TEXT, (track_x, thumb_y, 2, thumb_h))


def draw_modal(
    surf: pygame.Surface,
    font: pygame.font.Font,
    font_sm: pygame.font.Font,
    spec: ModalSpec,
    *,
    scroll: int = 0,
) -> ModalResult:
    """Modal paramétrico: título, subtítulo, columnas, scroll y barra de ayuda."""
    if spec.wide:
        bounds = pygame.Rect(
            MODAL_MARGIN,
            MODAL_MARGIN,
            surf.get_width() - MODAL_MARGIN * 2,
            surf.get_height() - MODAL_MARGIN * 2,
        )
    else:
        bounds = map_rect()

    if spec.dim_map:
        overlay = pygame.Surface((bounds.w, bounds.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, MODAL_DIM_ALPHA))
        surf.blit(overlay, (bounds.x, bounds.y))

    title = font.render(spec.title, False, spec.title_color) if spec.title else None
    subtitle = font_sm.render(spec.subtitle, False, COL_DIM) if spec.subtitle else None
    help_surface = font_sm.render(spec.help_text, False, COL_DIM) if spec.help_text else None

    rendered_columns: list[tuple[ModalColumn, pygame.Surface | None, list[tuple[ModalLine, pygame.Surface]]]] = []
    max_lines = 0
    row_step = font_sm.get_height() + 3
    has_headers = False
    for column in spec.columns:
        header = font_sm.render(column.header, False, COL_WARN) if column.header else None
        rendered = [(line, _render_line(line, font, font_sm)) for line in column.lines]
        rendered_columns.append((column, header, rendered))
        max_lines = max(max_lines, len(rendered))
        has_headers = has_headers or header is not None
        for line, surface in rendered:
            row_step = max(row_step, _line_step(line, surface))

    visible = spec.visible_lines if spec.visible_lines > 0 else max_lines
    visible = max(0, visible)
    max_scroll = max(0, max_lines - visible)
    scroll = max(0, min(scroll, max_scroll))

    title_h = (title.get_height() + 4) if title else 0
    subtitle_h = (subtitle.get_height() + 4) if subtitle else 0
    header_h = (font_sm.get_height() + 6) if has_headers else 0
    content_h = visible * row_step
    help_h = (help_surface.get_height() + MODAL_FOOTER_GAP + 1) if help_surface else 0

    box_w = bounds.w if spec.wide else max(spec.min_width, 0)
    box_h = MODAL_PAD_Y * 2 + title_h + subtitle_h + header_h + content_h + help_h
    if spec.fill_height:
        box_h = max(box_h, bounds.h)
    box_h = max(box_h, spec.min_height)
    box_h = min(box_h, bounds.h)
    box_w = min(max(box_w, spec.min_width), bounds.w)

    box = pygame.Rect(0, 0, box_w, box_h)
    box.center = bounds.center
    pygame.draw.rect(surf, COL_PANEL, box)
    pygame.draw.rect(surf, COL_BORDER, box, 2)

    y = box.y + MODAL_PAD_Y
    if title:
        surf.blit(title, (box.centerx - title.get_width() // 2, y))
        y += title_h
    if subtitle:
        surf.blit(subtitle, (box.centerx - subtitle.get_width() // 2, y))
        y += subtitle_h

    content_top = y + header_h
    content_bottom = box.bottom - MODAL_PAD_Y - help_h
    content_rect = pygame.Rect(
        box.x + MODAL_PAD_X,
        content_top,
        max(0, box.w - MODAL_PAD_X * 2),
        max(0, content_bottom - content_top),
    )

    column_count = max(1, len(rendered_columns))
    total_gap = MODAL_COLUMN_GAP * (column_count - 1)
    column_w = max(0, (content_rect.w - total_gap) // column_count)

    for index, (column, header, rendered) in enumerate(rendered_columns):
        column_x = content_rect.x + index * (column_w + MODAL_COLUMN_GAP)
        if header:
            header_x = column_x + (column_w - header.get_width()) // 2 if column.align == "center" else column_x
            surf.blit(header, (header_x, y))
        for row in range(visible):
            line_index = scroll + row
            if line_index >= len(rendered):
                break
            line, surface = rendered[line_index]
            if column.align == "center":
                x = column_x + (column_w - surface.get_width()) // 2
            else:
                x = column_x
            surf.blit(surface, (x, content_top + row * row_step))

    if max_scroll > 0 and content_rect.h > 0:
        draw_scrollbar(
            surf,
            box.right - 8,
            content_rect.y,
            content_rect.h,
            visible,
            max_lines,
            scroll,
        )

    if help_surface:
        help_top = box.bottom - MODAL_PAD_Y - help_surface.get_height()
        divider_y = help_top - MODAL_FOOTER_GAP
        pygame.draw.line(
            surf,
            COL_DIM,
            (box.x + MODAL_PAD_X, divider_y),
            (box.right - MODAL_PAD_X, divider_y),
        )
        surf.blit(help_surface, (box.centerx - help_surface.get_width() // 2, help_top))

    return ModalResult(box=box, content=content_rect, max_scroll=max_scroll)
