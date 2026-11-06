#!/usr/bin/env python3
"""Empaqueta la beta de PC (1x) para el sistema actual."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PLATFORM = "windows" if os.name == "nt" else "linux"
DIST = HERE / "dist" / PLATFORM
BUILD = HERE / "build" / PLATFORM
VARIANTS = (
    ("SolitudineBeta", "main.py"),
)


def main() -> None:
    import PyInstaller.__main__

    if DIST.exists():
        shutil.rmtree(DIST)
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)

    suffix = ".exe" if os.name == "nt" else ""
    for name, entry in VARIANTS:
        work = BUILD / name
        args = [
            str(HERE / entry),
            "--name",
            name,
            "--onefile",
            "--windowed",
            "--noconfirm",
            "--clean",
            "--noupx",
            "--paths",
            str(ROOT),
            "--paths",
            str(HERE),
            "--add-data",
            f"{ROOT / 'locales'}{os.pathsep}locales",
            "--distpath",
            str(DIST),
            "--workpath",
            str(work),
            "--specpath",
            str(work),
            "--log-level",
            "WARN",
        ]
        for asset in ("tiles", "modules", "icons", "fonts", "credits"):
            args.extend(
                [
                    "--add-data",
                    f"{ROOT / 'assets' / asset}{os.pathsep}assets/{asset}",
                ]
            )
        PyInstaller.__main__.run(args)

        exe = DIST / f"{name}{suffix}"
        if not exe.exists():
            raise SystemExit(f"No se generó {exe}")

        package = DIST / f"package-{name}"
        package.mkdir()
        shutil.copy2(exe, package / exe.name)
        shutil.copy2(HERE / "LEEME.txt", package / "LEEME.txt")

        if os.name == "nt":
            archive = shutil.make_archive(
                str(DIST / f"{name}-{PLATFORM}"),
                "zip",
                root_dir=package,
            )
        else:
            archive = shutil.make_archive(
                str(DIST / f"{name}-{PLATFORM}"),
                "gztar",
                root_dir=package,
            )
        print(f"Listo: {archive}")


if __name__ == "__main__":
    main()
