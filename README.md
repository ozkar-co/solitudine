# SOLITUDINE

Gestión y supervivencia en un planeta hostil: controlas la red de módulos y los recursos desde la consola del hábitat.

## Desarrollo (PC)

    make config
    make test
    .venv/bin/python main.py --dev
    .venv/bin/python main.py --dev --2x

`--dev` hace que el teclado emule el mando. `--2x` (solo PC con `--dev`) escala la ventana a 1280×960 para depurar. Controles y teclas en [docs/diseno-juego.md](docs/diseno-juego.md).

## Consola (PortMaster / R36S)

    make dist

Copiar a la SD:

    dist/Solitudine.sh   →  roms/ports/Solitudine.sh
    dist/solitudine/     →  roms/ports/solitudine/

La consola monta el runtime pygame-ce (squashfs) incluido en `port/runtime/`; no se usa Nuitka/PyInstaller. **SELECT+START** cierra el juego.

Más documentación en [docs/](docs/).
