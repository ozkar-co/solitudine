# SOLITUDINE

Juego de gestión / supervivencia en un planeta hostil. Controlas la red de módulos, recursos y automatización desde la consola del hábitat — sin salir al exterior. Inspiración: *Factorio*, *The Martian*, *Ur-Quan Masters* (radio final).

Documentación: [docs/diseno-juego.md](docs/diseno-juego.md) (diseño actual) · [docs/ideas.md](docs/ideas.md) (brainstorm original).

## Fases de desarrollo

| Fase | Estado | Descripción |
|------|--------|-------------|
| **0** | **Hecho** | Input mando (`LJOY_*`, `DPAD_*`, …) |
| **1** | **Hecho** | Mapa + cámara + cursor + panel + capas |
| **2** | **Hecho** | Simulación, construcción, supervivencia, game over |
| **3** | **Actual** | Buffers, depósitos finitos, mina, fabricador, almacén |
| 4+ | Pendiente | Eventos, investigación, finales |

## Requisitos (desarrollo en PC)

- Python 3.10+
- Dependencias en [requirements.txt](requirements.txt)

```bash
./scripts/run_dev.sh
```

Activa `SOLITUDINE_DEV=1`: el teclado emula el mando (solo en PC; no va en la SD).

| Teclas | Mando |
|--------|-------|
| Z / X / C / V | A / B / X / Y |
| Q / E / 1 / 2 | L1 / R1 / L2 / R2 |
| Backspace / Enter | SELECT / START |
| U / O / F | L3 / R3 / FN |
| I / K / J / L | DPAD_UP / DOWN / LEFT / RIGHT |
| WASD | LJOY_UP / DOWN / LEFT / RIGHT |
| Flechas | RJOY_UP / DOWN / LEFT / RIGHT |

Nombres estándar definidos en [src/gamepad.py](src/gamepad.py): `A`, `DPAD_*`, `LJOY_*`, `RJOY_*`, etc.

## Instalar en R36S (PortMaster)

```bash
./scripts/fetch_runtime.sh   # una vez (~22 MB)
./scripts/build_dist.sh
```

Copiar a la SD:

```
dist/Solitudine.sh   →  roms/ports/Solitudine.sh
dist/solitudine/     →  roms/ports/solitudine/
```

Input **directo** vía Pygame — no usa gptokeyb. **SELECT+START** cierra el juego.

## Mapeo de botones (R36S)

Definido en [src/gamepad.py](src/gamepad.py):

| btn | Nombre |
|-----|--------|
| 0–3 | A, B, X, Y |
| 4–5 | L1, R1 |
| 6–7 | L2, R2 |
| 8–9 | SELECT, START |
| 11–12 | L3, R3 |
| 13 | FN |
| 14–17 | DPAD_UP, DOWN, LEFT, RIGHT |

Botones: ver tabla en [src/gamepad.py](src/gamepad.py). Sticks: `LJOY_*` y `RJOY_*` (el hardware cruzado se resuelve solo ahí).

## Resolución

Pantalla fija **640×480** (R36S).

## Estructura del repo

```
solitudine/
├── docs/
│   ├── diseno-juego.md   # diseño actual — editar
│   └── ideas.md          # brainstorm original
├── src/
│   ├── main.py         # entrada
│   ├── game.py         # bucle principal
│   ├── simulation.py   # tiempo, recursos, game over
│   ├── construction.py # menú B, cables, módulos
│   ├── world.py        # mapa 1024×1024
│   ├── ui.py           # HUD + panel
│   ├── gamepad.py
│   └── locales/es.json
├── port/Solitudine.sh
├── scripts/
│   ├── fetch_runtime.sh
│   ├── build_dist.sh
│   └── run_dev.sh
└── dist/             # generado — copiar a SD
```
