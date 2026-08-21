# SOLITUDINE

Juego de gestión / supervivencia en un planeta hostil. Controlas la red de módulos, recursos y automatización desde la consola del hábitat — sin salir al exterior. Inspiración: *Factorio*, *The Martian*, *Ur-Quan Masters* (radio final).

Documentación: [docs/diseno-juego.md](docs/diseno-juego.md) (diseño) · [docs/arquitectura.md](docs/arquitectura.md) (código) · [docs/estado.md](docs/estado.md) (continuidad) · [docs/ideas.md](docs/ideas.md) (brainstorm).

## Fases de desarrollo

| Fase | Estado | Descripción |
|------|--------|-------------|
| **0** | **Hecho** | Input mando (`LJOY_*`, `DPAD_*`, …) |
| **1** | **Hecho** | Mapa + cámara + cursor + capas Terreno/Recursos (`X`) |
| **2** | **Hecho** | Simulación, construcción, supervivencia, game over |
| **3** | **Hecho** | Buffers, depósitos finitos, mina, fabricador, almacén |
| **3b** | **Hecho** | Logística proporcional, O₂ del invernadero, UX construcción (Y/B), panel transparente |
| 4+ | Pendiente | Laboratorio, investigación, O₂ sostenible, eventos, finales |

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

### Controles en juego

| Botón | Acción |
|-------|--------|
| `LJOY` / `DPAD` | Cursor |
| `RJOY` | Pan cámara |
| `L1` / `L2` | Zoom |
| `A` | Inspeccionar / colocar |
| `B` | Cancelar construcción |
| `X` | Capa Terreno ↔ Recursos |
| `Y` | Menú construcción (modal) |
| `START` | Pausa |

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
│   ├── diseno-juego.md   # diseño — qué hace el juego
│   ├── arquitectura.md   # código — dónde añadir cosas
│   ├── estado.md         # continuidad — retomar sin contexto
│   └── ideas.md          # brainstorm original
├── src/
│   ├── main.py         # entrada
│   ├── game.py         # bucle (orquestación)
│   ├── game_help.py    # ayuda contextual
│   ├── simulation.py   # tiempo, game over
│   ├── logistics.py    # caps de red + orquestación
│   ├── module_kind.py  # enum ModuleKind
│   ├── module_defs.py  # registro de módulos (flujos, costes)
│   ├── module_tick.py  # produce/consume por tick
│   ├── construction.py # construcción
│   ├── resources.py    # reservas hábitat
│   ├── module_flow.py  # panel → module_defs
│   ├── module_power.py # panel → module_defs
│   ├── game_input.py   # input por frame
│   ├── world.py        # mapa 1024×1024
│   ├── ui.py           # fachada HUD + modales
│   ├── ui_map.py       # mapa, tiles, preview
│   ├── ui_panel.py     # panel lateral
│   ├── ui_theme.py     # colores y layout
│   ├── ui_modals.py    # modales en mapa
│   ├── ui_input.py     # política de input
│   ├── gamepad.py
│   └── locales/es.json
├── port/Solitudine.sh
├── scripts/
│   ├── fetch_runtime.sh
│   ├── build_dist.sh
│   └── run_dev.sh
└── dist/             # generado — copiar a SD
```
