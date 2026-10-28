# Arquitectura de Solitudine

> Referencia para entender el código, tomar decisiones coherentes y saber **dónde** añadir funcionalidad nueva.
> Complementa [diseno-juego.md](diseno-juego.md) (qué debe hacer el juego) con **cómo** está organizado el código.

---

## Principios

| Principio | En la práctica |
|-----------|----------------|
| **KISS** | Sin frameworks ni capas innecesarias. Un `.py` = una responsabilidad clara. |
| **DRY** | Una sola fuente de verdad: balance en `config.py`, **flujos de módulos en `module_defs.py`**, textos en `locales/`, modales en `ui_modals.py`. |
| **Single Responsibility** | La simulación no dibuja; la UI no muta el mundo; `game.py` solo orquesta. |

---

## Vista general

```mermaid
flowchart TB
    subgraph entrada["Entrada"]
        main["main.py"]
        gamepad["gamepad.py / input_state.py"]
        dev["dev_input.py"]
    end

    subgraph orquestacion["Orquestación (1 frame)"]
        game["game.py"]
        ui_input["ui_input.py"]
        game_input["game_input.py"]
        game_help["game_help.py"]
    end

    subgraph modulos["Módulos (única fuente)"]
        module_kind["module_kind.py"]
        module_defs["module_defs.py"]
        module_tick["module_tick.py"]
    end

    subgraph sim["Simulación"]
        simulation["simulation.py"]
        logistics["logistics.py"]
        resources["resources.py"]
        materials["materials.py"]
        construction["construction.py"]
    end

    subgraph mundo["Mundo"]
        world["world.py"]
        network["network.py"]
        vision["vision.py"]
    end

    subgraph presentacion["Presentación"]
        ui["ui.py"]
        ui_map["ui_map.py"]
        ui_panel["ui_panel.py"]
        ui_theme["ui_theme.py"]
        ui_modals["ui_modals.py"]
        module_flow["module_flow.py"]
        module_power["module_power.py"]
    end

    main --> game
    game --> ui_input
    game --> simulation
    game --> construction
    game --> ui
    game --> game_input
    game --> game_help
    simulation --> logistics
    simulation --> construction
    logistics --> module_tick
    module_tick --> module_defs
    module_defs --> module_kind
    module_flow --> module_defs
    module_power --> module_defs
    logistics --> network
    construction --> world
    construction --> network
    construction --> vision
    ui --> ui_map
    ui --> ui_panel
    ui --> ui_theme
    ui --> ui_modals
    ui_panel --> ui_map
    ui --> module_flow
    ui --> module_power
    gamepad --> game
```

---

## Flujo de un frame (`game.py`)

Orden fijo cada iteración:

1. **Eventos** → `Input.poll()` (mando o teclado dev).
2. **Política de input** → `ui_input.input_policy()` (¿pausa tiempo? ¿bloquear cursor?).
3. **Acciones del jugador** → pausa, construcción, inspección, colocación.
4. **Simulación** → `Simulation.update(dt, world)` si no está pausado.
5. **Cámara y cursor** según política.
6. **Dibujado** → mapa, HUD, panel, modales encima.
7. **Ayuda contextual** → `game_help.context_help()`.

`game.py` **no** debe acumular lógica de negocio: solo enlaza subsistemas.

---

## Flujo de simulación (`simulation.py`)

Por tick (cuando no hay pausa ni game over):

1. Avanzar reloj (`day`, `day_progress`).
2. **`apply_modules_dt()`** — producción, consumo y energía proporcional (`module_tick.py` + `logistics.py`).
3. **`build.update_sites()`** — progreso de construcción (`construction.py`).
4. **`check_death()`** — game over si O₂/agua/comida = 0.

**Orden importante:** producir/consumir (incl. hábitat) → morir. El consumo vital del astronauta pasa por el módulo **hábitat** en `module_tick` (O₂, agua, comida y energía mínima).

---

## Capas y archivos

### Configuración e i18n

| Archivo | Responsabilidad |
|---------|-----------------|
| `config.py` | Constantes numéricas: caps, costes, tiempos, tamaño mapa. **Editar aquí** al balancear. |
| `locales/es.json` | Cadenas visibles al jugador. Claves usadas con `t("clave")` vía `i18n.py`. |
| `i18n.py` | Carga JSON de idioma. |

### Entrada

| Archivo | Responsabilidad |
|---------|-----------------|
| `gamepad.py` | Nombres semánticos de botones (`A`, `LJOY_UP`, …). |
| `input_state.py` | Estado del mando por frame (`held`, `pressed`). |
| `dev_input.py` | Teclado → mando en PC (`--dev`). |
| `ui_input.py` | **Política** de qué input está permitido según modo (pausa, menú construcción, game over). |

### Mundo y mapa

| Archivo | Responsabilidad |
|---------|-----------------|
| `world.py` | Grid 1024², tiles, depósitos, módulos, generación procedural. |
| `network.py` | Red logística (BFS desde hábitat). **`get_connected()`** cachea el resultado en `World`; invalidar al añadir cables o módulos. |
| `vision.py` | Niebla/explorado/visión clara (contadores incrementales). |
| `camera.py` | Pan, zoom, conversión tile ↔ pantalla. |

### Economía y supervivencia

| Archivo | Responsabilidad |
|---------|-----------------|
| `resources.py` | Reservas del hábitat (O₂, E, agua, comida) y consumo del astronauta. |
| `materials.py` | Componentes y mineral (stock de construcción). |
| `logistics.py` | Caps de red (`network_caps`) y orquestación del tick. |
| `module_kind.py` | Enum `ModuleKind` (sin dependencias — evita ciclos). |
| `module_defs.py` | **Registro de módulos**: flujos nominales, costes, colores, metadata. Panel y sim leen de aquí. |
| `module_tick.py` | Lógica de tick por módulo (produce/consume/energía). |
| `module_flow.py` / `module_power.py` | Delegados finos al panel → `module_defs`. |

### Construcción

| Archivo | Responsabilidad |
|---------|-----------------|
| `simulation.py` | Reloj, estado global (`game_over`, pausa), encadena los sistemas anteriores. |
| `game_input.py` | Acciones del jugador por frame (construcción, inspección, pausa). |

### UI (presentación)

| Archivo | Responsabilidad |
|---------|-----------------|
| `ui_theme.py` | Colores, `format_amount`, `alert_color`; re-exporta rects de `ui_layout`. |
| `ui_layout.py` | Regiones fijas 640×480: mapa, panel, barras. |
| `ui_assets.py` | Carga/caché de tiles, módulos, iconos y fuente VT323. |
| `ui_minimap.py` | Minimapa cacheado sobre la región explorada. |
| `ui_modals.py` | **`draw_map_modal()`** — recuadro centrado en el mapa (pausa, menú construcción, game over). |
| `ui_map.py` | Mapa: tiles, capas, cables, módulos, preview y cursor. |
| `ui_panel.py` | Panel lateral: inspección, hábitat, modo colocar. |
| `ui.py` | Fachada: HUD, modales, re-export de mapa/panel. |
| `module_flow.py` | Flujos diarios mostrados en panel (+O₂, −agua, …). Debe coincidir con `logistics.py`. |
| `module_power.py` | Balance E/día por módulo en panel. Debe coincidir con demanda en `logistics.py`. |
| `game_help.py` | Texto de la barra inferior según contexto. |

---

## UI: modales vs panel

| Situación | Dónde se muestra | Oscurece mapa |
|-----------|------------------|---------------|
| Elegir pieza (`BuildMode.MENU`) | Modal (`draw_build_menu_modal`) | Sí |
| Pausa (`user_paused`) | Modal (`draw_pause_modal`) | No |
| Game over | Modal (`draw_game_over`) | Sí |
| Colocar pieza (`BuildMode.PLACE`) | **Panel lateral** (coste, tiempo, validez) | No |

Todos los modales usan **`draw_map_modal()`** en `ui_modals.py`. Para un modal nuevo: construir `list[ModalLine]` y llamar a esa función.

---

## Guía: añadir funcionalidad

### Nuevo módulo constructible

1. **`config.py`** — constantes numéricas de balance (si hace falta valor nuevo).
2. **`module_defs.py`** — entrada en `MODULE_DEFS` (flujos, coste, buffer, depósito, color).
3. **`module_tick.py`** — handler de tick si el comportamiento no es trivial (extractor, invernadero, …).
4. **`module_kind.py`** — añadir valor al enum `ModuleKind`.
5. **`construction.py`** — `BuildKind` + entrada en `BUILD_TO_MODULE`.
6. **`vision.py`** — `module_radii()` si da visión.
7. **`locales/es.json`** — strings `build.*`, `module.*`, `flow.*`.
8. **`diseno-juego.md`** — si cambia diseño visible.

No duplicar flujos en `module_flow.py` ni `module_power.py` — solo delegan a `module_defs`.

### Nuevo recurso en la red

1. **`config.py`** — cap base, tasa, inicio.
2. **`resources.py`** o **`materials.py`** — pool y consumo.
3. **`logistics.py`** — caps en `_NetworkCaps`, producción y flush de buffers.
4. Panel hábitat en **`ui_panel.py`** (`_draw_habitat_resources`) y strings en locales.

### Nueva pantalla o modal

1. Definir líneas → **`ui_modals.draw_map_modal()`** (no duplicar cajas).
2. Llamar desde **`game.py`** después del dibujado base, mismo patrón que pausa/game over.
3. Si bloquea input: extender **`ui_input.input_policy()`**.
4. Ayuda contextual: **`game_help.context_help()`**.

### Nuevo control

1. **`game.py`** — manejar en el bloque de acciones (junto a Y/B/START).
2. **`game_help.py`** — texto de ayuda si cambia el contexto.
3. **`locales/es.json`** — `help.*`.
4. Documentar en **`diseno-juego.md`** (diseño) y esta guía si afecta arquitectura.

---

## Decisiones de diseño (registro)

Decisiones ya tomadas en código — conviene respetarlas al extender:

| Tema | Decisión |
|------|----------|
| Red logística | Un solo cable; BFS ortogonal desde hábitat; conectividad cacheada con `get_connected()`. |
| Energía | Demanda total de módulos activos; factor proporcional si falta E; inactivos no demandan. |
| Buffers | Productores paran (y no gastan E) si buffer + cap red llenos. |
| O₂ | Hábitat no produce; invernadero +2 O₂/d aunque comida llena (menor E si solo O₂). |
| Solar | `SOLAR_POWER_DAILY` = total diario; producción solo 6–18 h, repartida en esas horas. |
| Consumo hábitat | O₂/agua/comida/energía mínima vía módulo hábitat en `module_tick`; visible en panel. |
| Construcción | `Y` menú modal; colocar en panel + preview en mapa; `B` cancela; no pausa tiempo. |
| Visión | `explored` permanente; `visible` por contadores (no recomputo global). |
| Capas mapa | Terreno / Recursos (`X`); overlay semitransparente en explorado. |

---

## Anti-patrones (evitar)

- Duplicar constantes de balance fuera de `config.py`.
- Añadir producción en `game.py` o duplicar flujos fuera de `module_defs.py`.
- Crear otro dibujado de caja modal sin usar `ui_modals.py`.
- Meter strings en español hardcodeados en Python (usar `locales/`).
- Hacer que `module_flow`/`module_power` muestren valores distintos a lo que simula `logistics`.

---

## Estructura del repo (resumen)

Todos los `.py` y `locales/` viven en la raíz. `main.py` es la única entrada.

```
main.py                  # entry: argparse (--dev / --handheld)
game.py                  # bucle; orquestación
game_help.py             # ayuda contextual
simulation.py            # reloj + encadenar sistemas
module_kind.py           # enum ModuleKind
module_defs.py           # registro único de módulos
module_tick.py           # tick produce/consume
game_input.py            # input por frame
resources.py             # reservas hábitat
materials.py             # componentes / mineral
construction.py          # FSM construcción
world.py                 # mapa y entidades
network.py               # conectividad
vision.py                # niebla
camera.py
config.py                # balance numérico
ui.py                    # fachada HUD + modales
ui_map.py                # dibujado del mapa
ui_panel.py              # panel lateral
ui_layout.py             # regiones 640×480
ui_theme.py              # colores y formatos
ui_assets.py             # sprites, iconos y fuente
ui_minimap.py            # minimapa
ui_modals.py             # modales sobre mapa
ui_input.py              # política de input
module_flow.py           # panel: flujos
module_power.py          # panel: energía
i18n.py
gamepad.py / input_state.py / dev_input.py
locales/es.json
assets/                  # tiles, módulos, iconos, fuente y sources
port/
├── Solitudine.sh        # lanzador PortMaster
└── runtime/             # runtime pygame-ce versionado (squashfs)
```

`Makefile`: `make config` (venv + wheelhouse), `make fetch`, `make clean`, `make dist` (PortMaster). No hay `make run`; se ejecuta `.venv/bin/python main.py --dev`.

---

## Relación con otros documentos

| Documento | Uso |
|-----------|-----|
| [diseno-juego.md](diseno-juego.md) | Visión, mecánicas, fases, controles — **qué** construimos. |
| [arquitectura.md](arquitectura.md) | Este archivo — **dónde** va cada pieza de código. |
| [ideas.md](ideas.md) | Brainstorm histórico; no es fuente de verdad de implementación. |

Al cerrar una feature: actualizar diseño si cambia el comportamiento visible; actualizar arquitectura si cambia dónde vive la lógica o cómo extender el proyecto.
