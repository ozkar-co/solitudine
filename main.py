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
    args = parser.parse_args()
    return run(dev=args.dev, handheld=args.handheld)


if __name__ == "__main__":
    sys.exit(main())
