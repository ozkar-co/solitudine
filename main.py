#!/usr/bin/env python3
"""Solitudine — entrada del juego."""

import argparse
import os
import sys


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
    parser.add_argument(
        "--world-size",
        type=int,
        default=None,
        help="Lado del mapa en tiles (default: 2048 o SOLITUDINE_WORLD_SIZE).",
    )
    parser.add_argument(
        "--seed",
        default=None,
        help="Semilla fija para reproducir un mundo nuevo (default: aleatoria).",
    )
    args = parser.parse_args()
    if args.scale2 and not args.dev:
        parser.error("--2x requiere --dev")
    if args.scale2 and args.handheld:
        parser.error("--2x no aplica a --handheld")
    if args.world_size is not None:
        if args.world_size < 64:
            parser.error("--world-size debe ser >= 64")
        os.environ["SOLITUDINE_WORLD_SIZE"] = str(args.world_size)
    if args.seed is not None:
        if not args.seed.strip():
            parser.error("--seed no puede estar vacío")
        os.environ["SOLITUDINE_SEED"] = args.seed
    from game import run

    return run(dev=args.dev, handheld=args.handheld, scale=2 if args.scale2 else 1)


if __name__ == "__main__":
    sys.exit(main())
