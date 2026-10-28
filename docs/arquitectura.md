# Arquitectura

> Cómo está organizado el código. Qué debe hacer el juego: [diseno-juego.md](diseno-juego.md). Próximo trabajo: [plan.md](plan.md).

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
       │    ├─ construction.update_sites
       │    ├─ apply_modules_dt (logística/energía)
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
| `module_kind.py` | Enum de módulos. |
| `module_defs.py` | Registro de módulos, flujos, costes, `module_active()`. |
| `module_tick.py` | Tick: producción, consumo, energía y lámpara. |
| `module_flow.py` / `module_power.py` | Delegados finos del panel a `module_defs`. |
| `logistics.py` | Caps de red, buffers y orquestación del tick. |
| `resources.py` / `materials.py` | Reservas vitales / stock de construcción. |
| `construction.py` | Menú, preview y colocación. |
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
| `ui_modals.py` | Modales (pausa, construcción, game over). |
| `ui_input.py` / `game_help.py` | Política de input / texto contextual. |
| `ui.py` | HUD, modales y fachada de mapa/panel. |
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
9. Tests en `test_sim.py`.

## Guardado

- `save.json` junto al ejecutable; ignorado por git.
- Guarda simulación, recursos, stock, módulos/cables, `enabled` y arrays del mundo comprimidos.
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
