"""Datos de créditos — nombres y roles, sin lógica de UI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CreditEntry:
    name_key: str
    role_key: str


CREDITS_SECTIONS: tuple[tuple[str, tuple[CreditEntry, ...]], ...] = (
    (
        "credits.section_team",
        (
            CreditEntry("credits.ozkr_name", "credits.ozkr_roles"),
            CreditEntry("credits.deepseek_name", "credits.deepseek_roles"),
            CreditEntry("credits.retro_name", "credits.retro_roles"),
            CreditEntry("credits.juandi_name", "credits.juandi_roles"),
            CreditEntry("credits.neozound_name", "credits.neozound_roles"),
            CreditEntry("credits.laura_name", "credits.laura_roles"),
        ),
    ),
    (
        "credits.section_support",
        (
            CreditEntry("credits.neo_cleo_name", "credits.neo_cleo_roles"),
        ),
    ),
    (
        "credits.section_thanks",
        (
            CreditEntry("credits.oss_name", "credits.oss_roles"),
            CreditEntry("credits.python_name", "credits.python_roles"),
            CreditEntry("credits.pygame_name", "credits.pygame_roles"),
            CreditEntry("credits.portmaster_name", "credits.portmaster_roles"),
        ),
    ),
    (
        "credits.section_licenses",
        (
            CreditEntry("credits.python_license_name", "credits.python_license_roles"),
            CreditEntry("credits.pygame_license_name", "credits.pygame_license_roles"),
            CreditEntry("credits.font_name", "credits.font_roles"),
        ),
    ),
)

CREDITS_VISIBLE_LINES = 14
CREDITS_SCROLL_STEP = 3

KONAMI_SEQUENCE = ("UP", "UP", "DOWN", "DOWN", "LEFT", "RIGHT", "LEFT", "RIGHT")

CREDITS_LINE_COUNT = sum(1 + len(entries) * 2 for _section, entries in CREDITS_SECTIONS)


def max_credits_scroll() -> int:
    return max(0, CREDITS_LINE_COUNT - CREDITS_VISIBLE_LINES)


def advance_konami(progress: int, action: str | None) -> tuple[int, bool]:
    """Avanza la secuencia y devuelve (progreso, completada)."""
    if action is None:
        return progress, False
    if progress >= len(KONAMI_SEQUENCE):
        progress = 0
    if action == KONAMI_SEQUENCE[progress]:
        progress += 1
    elif action == KONAMI_SEQUENCE[0]:
        progress = 1
    else:
        progress = 0
    if progress >= len(KONAMI_SEQUENCE):
        return 0, True
    return progress, False
