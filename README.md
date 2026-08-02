# SOLITUDINE

Juego de gestión / supervivencia en un planeta hostil. Controlas la red de módulos, recursos y automatización desde la consola del hábitat — sin salir al exterior. Inspiración: *Factorio*, *The Martian*, *Ur-Quan Masters* (radio final).

Documento de diseño completo: [ideas.md](ideas.md).

## Fases de desarrollo

| Fase | Estado | Descripción |
|------|--------|-------------|
| **0** | **Actual** | Depurador de mando directo (sin gptokeyb) |
| 1 | Pendiente | UI base 640×480, panel + diagrama ASCII |
| 2 | Pendiente | Grafo simple: 3 nodos, energía y comida |
| 3+ | Pendiente | Desgaste, investigación, exploración, finales |

## Requisitos (desarrollo en PC)

- Python 3.10+
- Dependencias en [requirements.txt](requirements.txt)

```bash
./scripts/run_dev.sh
```

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

Input **directo** vía Pygame — no usa gptokeyb. Sal con el atajo de la consola.

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

Los ejes analógicos se muestran en vivo; anota qué `ax0`, `ax1`… corresponde a cada stick para completar el mapeo.

## Resolución

Pantalla fija **640×480** (R36S).

## Estructura del repo

```
solitudine/
├── src/
│   ├── main.py       # depurador fase 0
│   └── gamepad.py    # nombres de botones / deadzone
├── port/Solitudine.sh
├── scripts/
│   ├── fetch_runtime.sh
│   ├── build_dist.sh
│   └── run_dev.sh
└── dist/             # generado — copiar a SD
```
