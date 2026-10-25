#!/usr/bin/env python3
"""Solitudine — entrada del juego."""

import argparse
import os
import sys

from game import run


def main() -> int:
    parser = argparse.ArgumentParser(description="Solitudine.")
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Modo desarrollo: el teclado emula el mando (solo en PC).",
    )
    args = parser.parse_args()

    if args.dev:
        os.environ["SOLITUDINE_DEV"] = "1"

    return run()


if __name__ == "__main__":
    sys.exit(main())
