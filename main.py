#!/usr/bin/env python3
"""Solitudine — entrada del juego."""

import argparse
import sys

from game import run


def main() -> int:
    parser = argparse.ArgumentParser(description="Solitudine.")
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Modo desarrollo: el teclado emula el mando (solo en PC).",
    )
    parser.add_argument(
        "--handheld",
        action="store_true",
        help="Modo consola (PortMaster): pantalla completa escalada.",
    )
    parser.add_argument(
        "--2x",
        dest="scale2",
        action="store_true",
        help="Solo PC y --dev: renderiza la ventana al doble de tamaño.",
    )
    args = parser.parse_args()
    if args.scale2 and not args.dev:
        parser.error("--2x requiere --dev")
    if args.scale2 and args.handheld:
        parser.error("--2x no aplica a --handheld")
    return run(dev=args.dev, handheld=args.handheld, scale=2 if args.scale2 else 1)


if __name__ == "__main__":
    sys.exit(main())
