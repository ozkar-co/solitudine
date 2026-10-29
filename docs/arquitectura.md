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

## Archivos

| Archivo | Responsabilidad |
|---------|-----------------|
| `main.py` | Entrada; `--dev`, `--handheld`. |
| `game.py` | Bucle, cámara, HUD, pausa, game over y auto-save. |
| `simulation.py` | Reloj, día, pausa, muerte y estado global. |
| `config.py` | Balance numérico y layout. |
| `world.py` | Mapa, tiles, depósitos, módulos, cables y visión. |
| `tech_defs.py` | 2 tecnologías del slice y mapeo módulo → tecnología. |
| `research.py` | Investigación activa, progreso, desbloqueos y laboratorio. |
| `module_kind.py` | Enum de módulos. |
| `module_defs.py` | Registro de módulos, flujos, costes, `module_active()`. |
| `module_tick.py` | Tick: producción, consumo, energía y lámpara. |
| `module_flow.py` / `module_power.py` | Delegados finos del panel a `module_defs`. |
| `logistics.py` | Caps de red, buffers y orquestación del tick. |
| `resources.py` / `materials.py` | Reservas vitales / stock de construcción. |
| `construction.py` | Menú por pestañas, preview, bloqueo por tecnología y colocación. |
| `network.py` | Conectividad BFS cacheada. |
| `vision.py` | Niebla y visión incremental; respeta `enabled`. |
| `daylight.py` | Curva de luz natural. |
| `camera.py` | Cámara y zoom entero. |
| `savegame.py` | Guardado JSON con arrays comprimidos. |
| `game_input.py` | Acciones por frame, construcción, R1. |
| `input_state.py` / `gamepad.py` / `dev_input.py` | Entrada unificada. |
| `i18n.py` / `locales/es.json` | Textos. |
| `ui_layout.py` | Regiones 640×480. |
| `ui_theme.py` | Colores y formatos. |
| `ui_assets.py` | Sprites, iconos y fuente VT323. |
| `ui_map.py` | Tiles, cables, módulos, preview y dithering. |
| `ui_minimap.py` | Minimapa cacheado. |
| `ui_night.py` | Fuentes de luz visual y dithering por tile. |
| `ui_panel.py` | Inspección y modo colocar. |
| `ui_tech.py` | Pantalla de Tecnología mínima. |
| `ui_modals.py` | Modales (pausa, créditos, construcción, game over). |
| `ui_input.py` / `game_help.py` | Política de input / texto contextual. |
| `ui.py` | HUD, modales, badges de modo y fachada de mapa/panel. |
| `credits.py` | Datos de créditos y secuencia Konami; sin lógica de UI. |
| `test_sim.py` | Tests de regresión. |

## Reglas de UI

- Layout en `ui_layout.py`; nada de rects mágicos.
- Textos siempre por `t()`.
- La UI no modifica `sim`/`world`; `game_input.py` aplica acciones.
- No crear `ui_state`, `ui_widgets` ni `ui_console` hasta que existan varias pantallas.
- Dithering por tile; no alpha por frame.

## Añadir un módulo

1. `config.py`: constantes de coste, obra, flujos y radio de luz si aplica.
2. `module_kind.py`: valor en `ModuleKind`.
3. `module_defs.py`: entrada en `MODULE_DEFS` y `BUILDABLE_KINDS`.
4. `construction.py`: `BuildKind`, `BUILD_KINDS` y `BUILD_TO_MODULE`.
5. `module_tick.py`: handler solo si el flujo no es trivial.
6. `ui.py` / `ui_panel.py`: etiqueta del menú.
7. `locales/es.json`: `build.*`, `module.*`.
8. `assets/`: sprite final 16×16 + source; registrar en [assets.md](assets.md).
9. Si una tecnología lo desbloquea, añadir `TechDef.unlock_kind` en `tech_defs.py` y la fila en [catalogo.md](catalogo.md).
10. Tests en `test_sim.py`.

## Tecnología

- `tech_defs.py` define los nodos; `research.py` guarda activo/progreso/desbloqueos.
- `start_research()` exige laboratorio activo, energía y gasta componentes.
- El progreso escala con el factor de energía; si el laboratorio se apaga o desconecta, se pausa.
- `construction.kind_locked()` consulta las tecnologías desbloqueadas para el menú y la colocación.
- La pantalla `ui_tech.py` es una lista simple; no hay consola multipestaña.

## Guardado

- `save.json` junto al ejecutable; ignorado por git.
- Guarda simulación, recursos, stock, módulos/cables, `enabled`, investigación y arrays del mundo comprimidos.
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
- Añadir dependencias sin justificarlo.
