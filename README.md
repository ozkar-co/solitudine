# SOLITUDINE

Juego de gestión / supervivencia en un planeta hostil. Controlas la red de módulos, recursos y automatización desde la consola del hábitat — sin salir al exterior. Inspiración: *Factorio*, *The Martian*, *Ur-Quan Masters* (radio final).

Documento de diseño completo: [ideas.md](ideas.md).

## Fases de desarrollo

| Fase | Estado | Descripción |
|------|--------|-------------|
| **0** | **Actual** | Depurador de entrada (teclado + mando vía gptokeyb) |
| 1 | Pendiente | UI base 640×480, panel + diagrama ASCII |
| 2 | Pendiente | Grafo simple: 3 nodos, energía y comida |
| 3+ | Pendiente | Desgaste, investigación, exploración, finales |

## Requisitos (desarrollo en PC)

- Python 3.10+
- Dependencias en [requirements.txt](requirements.txt)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

O con el script:

```bash
./scripts/run_dev.sh
```

## Instalar en R36S (PortMaster)

### 1. Generar paquete

```bash
./scripts/build_dist.sh
```

### 2. Copiar a la SD

```
dist/Solitudine.sh   →  roms/ports/Solitudine.sh
dist/solitudine/     →  roms/ports/solitudine/
```

Estructura final en la SD:

```
roms/ports/
├── Solitudine.sh
└── solitudine/
    ├── main.py
    ├── solitudine.gptk
    └── log.txt          (se crea al ejecutar)
```

### 3. Python / Pygame en la consola

El script intenta `python3` del sistema. Si no hay pygame instalado, añade el runtime opcional:

```
roms/ports/solitudine/runtime/pygame-ce.squashfs
```

Puedes generarlo con [pygame-ce-runtime](https://github.com/viniciusfs/pygame-ce-runtime) o instalar pygame en el firmware si tu CFW lo permite.

### 4. Probar

1. Abre PortMaster → **Solitudine**
2. Pulsa teclas del mando; deben aparecer como eventos de teclado en pantalla
3. Si falla, revisa `roms/ports/solitudine/log.txt`

## Controles (fase 0)

En PC: cualquier tecla se muestra en pantalla. **ESC** o **Q** para salir.

En R36S, `gptokeyb` traduce el mando a teclado según [port/solitudine.gptk](port/solitudine.gptk):

| Mando | Tecla simulada |
|-------|----------------|
| Cruceta | Flechas |
| A / B / X / Y | Space / Z / X / C |
| L1–R2, L3, R3 | Q W E R T Y |
| Start | Enter |
| Select (back) | Escape |
| Stick izquierdo | WASD |
| Stick derecho | IJKL |

Si un botón no responde, edita `solitudine.gptk`, vuelve a ejecutar `build_dist.sh` y copia de nuevo.

## Resolución

Pantalla fija **640×480** (R36S). Desarrolla siempre a esa resolución.

## Estructura del repo

```
solitudine/
├── README.md
├── requirements.txt
├── ideas.md
├── src/main.py           # código del juego
├── port/                 # plantillas PortMaster
│   ├── Solitudine.sh
│   └── solitudine.gptk
├── scripts/
│   ├── build_dist.sh     # genera dist/
│   └── run_dev.sh        # prueba en PC
└── dist/                 # generado — copiar a SD
```
