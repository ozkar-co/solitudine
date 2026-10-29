# Arquitectura

> Cómo está organizado el código. Juego: [diseno-juego.md](diseno-juego.md). Roadmap: [plan.md](plan.md). Catálogo: [catalogo.md](catalogo.md).

## Principios

- Un archivo, una responsabilidad.
- La simulación no dibuja; la UI no muta el mundo; `game.py` orquesta.
- `module_defs.py` es la fuente única de módulos, flujos y costes.
- Sin abstracciones “por si acaso”: primero la función, luego el helper si se repite.
- Todo el `.py` está en la raíz; `main.py` es la única entrada.

## Flujo de un frame

```
main.py
  └─ game.run()
       ├─ input_policy / handle_frame_input
       ├─ simulation.update(dt, world)
       │    ├─ apply_modules_dt (logística/energía)
       │    ├─ research.advance si hay laboratorio activo
       │    ├─ construction.update_sites
       │    └─ muerte / game over
       ├─ draw_map / draw_minimap / draw_top_bar / draw_panel
       └─ modales / flip / clock.tick(60)
```

## Arranque

```
main.py → game.run()
  ├─ i18n
  ├─ pygame.display.init + pygame.font.init
  ├─ create_display + splash (pygame, sin assets)
  ├─ ui_assets.load
  ├─ savegame.load_game / generate_world
  ├─ pygame.joystick.init
  ├─ splash "Pulsa START" + espera
  └─ primer frame
```

El lanzador intenta un splash de texto en `tty1`/`tty0`/`console` antes de montar el runtime; es best-effort y puede no verse si el CFW mantiene EmulationStation en pantalla. El splash gráfico usa pygame en cuanto hay display, se mantiene hasta terminar la carga y espera START. Un splash gráfico previo requeriría un helper nativo/framebuffer y validación por dispositivo.

En PC, `--dev --2x` mantiene el render interno en 640×480 y escala la ventana a 1280×960 con `present()` (`pygame.transform.scale`). La consola sigue a 1x.

## Archivos

| Archivo | Responsabilidad |
|---------|-----------------|
| `main.py` | Entrada; `--dev`, `--handheld`, `--2x`. |
| `game.py` | Bucle, cámara, HUD, pausa, game over y auto-save. |
| `simulation.py` | Reloj, día, pausa, muerte y estado global. |
| `config.py` | Balance numérico y layout. |
| `world.py` | Mapa, tiles, depósitos, módulos, cables, ruinas y visión. |
| `tech_defs.py` | Nodos de tecnología y mapeo módulo → tecnología. |
| `research.py` | Investigación activa, progreso, desbloqueos y laboratorio. |
| `module_kind.py` | Enum de módulos. |
| `module_defs.py` | Registro de módulos, flujos, costes, `module_active()`. |
| `module_tick.py` | Tick: producción, consumo, energía y lámpara. |
| `module_flow.py` / `module_power.py` | Delegados finos del panel a `module_defs`. |
| `logistics.py` | Caps de red, buffers y orquestación del tick. |
| `resources.py` | Registro de recursos, pool único, `Cost` multi-material, caps y alertas. |
| `stats.py` | Contadores de chatarra procesada/reciclada. |
| `construction.py` | Menú por pestañas, preview, `cost_paid`, bloqueo por tecnología y colocación. |
| `demolition.py` | Demolición, cancelación de obra y conversión a ruina/chatarra. |
| `network.py` | Conectividad BFS cacheada. |
| `vision.py` | Niebla y visión incremental; respeta `enabled`. |
| `daylight.py` | Curva de luz natural. |
| `camera.py` | Cámara y zoom entero. |
| `savegame.py` | Guardado JSON v4 con arrays comprimidos; sin migración. |
| `game_input.py` | Acciones por frame, construcción, ruinas, demolición, R1. |
| `input_state.py` / `gamepad.py` / `dev_input.py` | Entrada unificada. |
| `i18n.py` / `locales/es.json` | Textos. |
| `ui_layout.py` | Regiones 640×480. |
| `ui_theme.py` | Colores y formatos. |
| `ui_assets.py` | Sprites, iconos, ruina y fuente VT323. |
| `ui_map.py` | Tiles, ruinas, cables, módulos, preview y dithering. |
| `ui_minimap.py` | Minimapa cacheado. |
| `ui_night.py` | Fuentes de luz visual y dithering por tile. |
| `ui_panel.py` | Inspección, ruinas, reciclador y modo colocar. |
| `ui_tech.py` | Pantalla de Tecnología mínima. |
| `ui_modals.py` | Modales reutilizables (pausa, créditos, construcción, game over). |
| `ui_input.py` / `game_help.py` | Política de input / texto contextual. |
| `ui.py` | HUD, modales (incluida demolición), badges de modo y fachada de mapa/panel. |
| `credits.py` | Datos de créditos y secuencia Konami; sin lógica de UI. |
| `test_sim.py` | Tests de regresión. |

## Reglas de UI

- Layout en `ui_layout.py`; nada de rects mágicos.
- Textos siempre por `t()`.
- La UI no modifica `sim`/`world`; `game_input.py` aplica acciones.
- No crear `ui_state`, `ui_widgets` ni `ui_console` hasta que existan varias pantallas.
- Dithering por tile; no alpha por frame.

## Añadir un módulo

1. `config.py`: coste como dict multi-material, obra, flujos y radio de luz si aplica.
2. `module_kind.py`: valor en `ModuleKind`.
3. `module_defs.py`: entrada en `MODULE_DEFS` y `BUILDABLE_KINDS` con `cost=Cost(...)`.
4. `construction.py`: `BuildKind`, `BUILD_KINDS` y `BUILD_TO_MODULE`.
5. `module_tick.py`: handler solo si el flujo no es trivial.
6. `ui.py` / `ui_panel.py`: etiqueta del menú y del panel.
7. `locales/es.json`: `build.*`, `module.*`, `module_desc.*`, `flow.*`.
8. `assets/`: sprite final 16×16 + source; registrar en [assets.md](assets.md). Si el módulo usa un recurso nuevo, añadir icono y entrada en `resources.py`.
9. Si una tecnología lo desbloquea, añadir `TechDef.unlock_kind` en `tech_defs.py` y la fila en [catalogo.md](catalogo.md).
10. Tests en `test_sim.py`.

## Tecnología

- `tech_defs.py` define los nodos; `research.py` guarda activo/progreso/desbloqueos.
- `start_research()` exige laboratorio activo, energía y gasta el `Cost` multi-material del nodo (`reciclaje` incluye chatarra).
- El progreso escala con el factor de energía; si el laboratorio se apaga o desconecta, se pausa.
- `construction.kind_locked()` consulta las tecnologías desbloqueadas para el menú y la colocación.
- La pantalla `ui_tech.py` es una lista simple; no hay consola multipestaña.

## Guardado

- `save.json` junto al ejecutable; ignorado por git.
- `VERSION` 4. Guarda simulación, los siete recursos, `stats`, módulos/cables, `cost_paid`, `enabled`, investigación, ruinas y arrays del mundo comprimidos.
- Sin migración: si el save no es v4, se borra al cargar y se empieza de cero.
- Auto-save al pausar, cambiar de día o salir; carga al iniciar.
- Si cambia el esquema, subir `VERSION` en `savegame.py`.

## Luz

- `light_sources()` devuelve hábitat y lámparas activas; un módulo apagado no ilumina.
- `tile_level()` calcula dithering 0..7; `dither_pattern()` cachea por nivel y tamaño.
- La lámpara consume energía en `module_tick` según `darkness(hour)`; la luz no altera producción.

## Anti-patrones

- Duplicar flujos en `module_flow.py`/`module_power.py`: delegar a `module_defs`.
- Recalcular el mundo completo por frame.
- Meter lógica de negocio en `ui_*`.
- Crear pantallas vacías o abstracciones para features futuras.
- Separar de nuevo el stock de materiales del pool de recursos o volver a costes `float` de un solo material.
- Añadir dependencias sin justificarlo.
