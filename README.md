# SOLITUDINE

Gestión y supervivencia en un planeta hostil: controlas la red de módulos y los recursos desde la consola del hábitat.

## Desarrollo (PC)

    make config
    .venv/bin/python main.py --dev

`--dev` hace que el teclado emule el mando. Controles y teclas en [docs/diseno-juego.md](docs/diseno-juego.md).

## Consola (PortMaster / R36S)

    make port

Copiar a la SD:

    dist/Solitudine.sh   →  roms/ports/Solitudine.sh
    dist/solitudine/     →  roms/ports/solitudine/

La consola monta un runtime pygame-ce (squashfs): el `make dist` de Nuitka/PyInstaller no aplica. **SELECT+START** cierra el juego.

Más documentación en [docs/](docs/).
