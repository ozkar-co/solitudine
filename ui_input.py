"""Política de entrada según modo UI — extensible a futuros menús."""

from __future__ import annotations

from dataclasses import dataclass

from construction import BuildMode, BuildController


@dataclass(frozen=True)
class InputPolicy:
    block_cursor: bool = False
    block_camera_pan: bool = False
    pause_time: bool = False


def input_policy(
    build: BuildController,
    *,
    game_over: bool = False,
    user_paused: bool = False,
    tech_open: bool = False,
) -> InputPolicy:
    if game_over or user_paused or tech_open:
        return InputPolicy(block_cursor=True, block_camera_pan=True, pause_time=True)
    if build.mode == BuildMode.MENU:
        return InputPolicy(block_cursor=True, block_camera_pan=True, pause_time=True)
    if build.mode == BuildMode.PLACE:
        return InputPolicy(pause_time=True)
    return InputPolicy()
