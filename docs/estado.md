# Estado del proyecto

> Punto de entrada para retomar el trabajo sin contexto previo. Actualizar al cerrar una sesión relevante.

**Última actualización:** 2026-10-28

## Dónde estamos

| Fase | Estado |
|------|--------|
| 0–3b | **Hecho** — mapa, simulación, construcción, logística, buffers, depósitos finitos, UX construcción |
| UI | **UI-0 hecho** — grilla, assets, minimapa, día/noche y lámpara; faltan scroll/consola |
| 4 | **4A hecho** — apagado, guardado y tests; faltan 4B/4C — ver [plan-fase4.md](plan-fase4.md) |
| 5 | **Diseñado, sin implementar** — ver [plan-fase5.md](plan-fase5.md): alimañas, tower defense, botín, inventario y muerte |
| 6+ | **Pendiente** — desgaste, eventos climáticos, radio y finales |

El código está aplanado en la raíz (sin `src/`). El juego es jugable en PC (`make config` + `.venv/bin/python main.py --dev`) y en R36S vía PortMaster (`make dist`).

## Próximo trabajo sugerido

1. **UI-1 restante** — panel con scroll y barra de acciones más explícita.
2. **UI-2** — consola con pestañas y huecos para tecnología/inventario/amenaza.
3. **Slice 4B** — laboratorio + 4 tecnologías.
4. **Slice 4C** — electrólisis, condensador, reciclaje y batería.
5. **Slice 5A** — inventario genérico y catálogo de muerte.

El orden y los criterios están en [plan-ui.md](plan-ui.md), [plan-fase4.md](plan-fase4.md) y [plan-fase5.md](plan-fase5.md). No abrir un slice nuevo sin cerrar y probar el anterior.

## Mapa de documentación

| Archivo | Cuándo leerlo |
|---------|----------------|
| [diseno-juego.md](diseno-juego.md) | Qué debe hacer el juego, balance de piezas, controles |
| [plan-ui.md](plan-ui.md) | Siguiente etapa — layout, assets pixel, consola y HUD |
| [assets.md](assets.md) | Prompts, seeds y regeneración de assets |
| [plan-fase4.md](plan-fase4.md) | Decisión vigente — UI, apagado, tecnología y recursos |
| [plan-fase5.md](plan-fase5.md) | Siguiente capa — alimañas, tower defense, botín, inventario y muerte |
| [arquitectura.md](arquitectura.md) | Dónde va código nuevo, flujo de frame/tick |
| [estado.md](estado.md) | Este archivo — continuidad entre sesiones |
| [ideas.md](ideas.md) | Brainstorm original; **no** es fuente de verdad de implementación |

## Archivos clave en código

| Qué | Dónde |
|-----|--------|
| Balance numérico | `config.py` |
| Flujos/costes de módulos | `module_defs.py` |
| Tick produce/consume | `module_tick.py` |
| Conectividad (caché) | `network.py` → `get_connected()` |
| Construcción | `construction.py` |
| Bucle principal | `game.py` |
| Textos UI | `locales/es.json` |
| Sprites/fuente | `assets/` |
| Registro de assets | `docs/assets.md` |
| Guardado | `savegame.py` (ignorado: `save.json`) |
| Tests | `test_sim.py` |

## Decisiones recientes

- UI dividida: `ui_map.py` (mapa), `ui_panel.py` (panel), `ui.py` (HUD + modales).
- Red: BFS cacheado; invalidar al colocar cable o módulo.
- Solar: 12 E/día nominal, repartido solo en horas 6–18 (un panel cubre hábitat 8 E/d).
- Capa mapa **Recursos** (sin subtítulo “subsuelo” en UI).
- Aplanado: todos los `.py` y `locales/` viven en la raíz; `main.py` es la única entrada (`--dev`, `--handheld`).
- Runtime pygame-ce versionado en `port/runtime/` (sin descarga en `make dist`).
- Fase 4: vertical slice (no contenido masivo). Apagado con `enabled`, árbol de tecnología como DAG de datos y consola a pantalla completa, sin recurso “ciencia” ni recursos nuevos.
- La regla de los seis: no añadir recursos hasta que los 6 actuales tengan ≥2 fuentes y ≥2 usos.
- Guardado JSON mínimo antes de expandir el árbol de tecnologías.
- Fase 5: combate automático por capas; el radar explora y atrae alimañas con un radio oculto; el inventario se generaliza antes de añadir botín.
- UI-0: grilla 16 px, zoom entero 1×/2×/3× (16/32/48), panel de 192 px, sprites de Genkit, minimapa R2, VT323 y barra de vitales. La UI va antes que las fases 4 y 5.
- Assets: RD Tile para terreno, RD+ para módulos/iconos; finales 16×16 y sources 32×32; registro en `docs/assets.md`.
- HUD: etiquetas completas Agua/Comida/Energía. `Comida` y `Energía` bajan a 8/día; el agua a 10/día por soporte vital. Componentes no tiene drenaje pasivo: solo cambia al construir o con fabricador.
- Día/noche: dithering de 8 niveles con colorkey (sin alpha), solo sobre el terreno; módulos, cables y cursor quedan brillantes. Coste medido despreciable en headless.
- Luz artificial visual: el hábitat ilumina radio 8 desde el inicio; la lámpara es un módulo construible de radio 10. La luz solo reduce el dithering nocturno y no altera producción. La lámpara consume energía solo de noche, proporcional a la oscuridad (máx. 4/día). Cálculo por tile visible, sin mapa global.
- Apagado: `Module.enabled` + `module_active()`. R1 apaga/enciende el módulo seleccionado (excepto hábitat); un módulo apagado no produce, no consume energía, no aporta visión, no suma cap de almacén, no emite luz y no vacía buffers.
- Guardado: `savegame.py` con JSON + arrays comprimidos; auto-save al pausar/cambiar de día/salir y carga al iniciar. `save.json` está ignorado por git. Versión de esquema 1.

## Comandos habituales

```bash
make config                        # venv + dependencias desde wheelhouse/
make test                          # tests de regresión
.venv/bin/python main.py --dev     # PC, teclado como mando
python3 -m py_compile *.py         # verificar sintaxis
make dist                          # empaquetar para R36S
```

## Verificación manual útil

- 10 invernaderos con O₂=0 y comida llena → +20 O₂/d neto.
- 1 panel solar conectado → reserva de E estable o sube de día.
