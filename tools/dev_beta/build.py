#!/usr/bin/env python3
"""Empaqueta la beta de PC para el sistema actual."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
NAME = "SolitudineBeta"
PLATFORM = "windows" if os.name == "nt" else "linux"
DIST = HERE / "dist" / PLATFORM
BUILD = HERE / "build" / PLATFORM


def main() -> None:
    import PyInstaller.__main__

    if DIST.exists():
        shutil.rmtree(DIST)
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)

    args = [
        str(HERE / "main.py"),
        "--name",
        NAME,
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--clean",
        "--noupx",
        "--paths",
        str(ROOT),
        "--add-data",
        f"{ROOT / 'locales'}{os.pathsep}locales",
        "--distpath",
        str(DIST),
        "--workpath",
        str(BUILD),
        "--specpath",
        str(BUILD),
        "--log-level",
        "WARN",
    ]
    for name in ("tiles", "modules", "icons", "fonts", "credits"):
        args.extend(
            [
                "--add-data",
                f"{ROOT / 'assets' / name}{os.pathsep}assets/{name}",
            ]
        )
    PyInstaller.__main__.run(args)

    suffix = ".exe" if os.name == "nt" else ""
    exe = DIST / f"{NAME}{suffix}"
    if not exe.exists():
        raise SystemExit(f"No se generó {exe}")

    package = DIST / "package"
    package.mkdir()
    shutil.copy2(exe, package / exe.name)
    shutil.copy2(HERE / "LEEME.txt", package / "LEEME.txt")

    if os.name == "nt":
        archive = shutil.make_archive(
            str(DIST / f"{NAME}-windows"),
            "zip",
            root_dir=package,
        )
    else:
        archive = shutil.make_archive(
            str(DIST / f"{NAME}-linux"),
            "gztar",
            root_dir=package,
        )
    print(f"Listo: {archive}")


if __name__ == "__main__":
    main()
