# Estado del proyecto

> Punto de entrada para retomar el trabajo sin contexto previo. Actualizar al cerrar una sesión relevante.

**Última actualización:** 2026-10-28

## Dónde estamos

| Fase | Estado |
|------|--------|
| 0–3b | **Hecho** — mapa, simulación, construcción, logística, buffers, depósitos finitos, UX construcción |
| UI | **Siguiente** — ver [plan-ui.md](plan-ui.md): grilla 16 px, assets pixel, consola y HUD |
| 4 | **Decidido, sin implementar** — ver [plan-fase4.md](plan-fase4.md): apagado, consola, tecnología y matriz de recursos |
| 5 | **Diseñado, sin implementar** — ver [plan-fase5.md](plan-fase5.md): alimañas, tower defense, botín, inventario y muerte |
| 6+ | **Pendiente** — desgaste, eventos climáticos, radio y finales |

El código está aplanado en la raíz (sin `src/`). El juego es jugable en PC (`make config` + `.venv/bin/python main.py --dev`) y en R36S vía PortMaster (`make dist`).

## Próximo trabajo sugerido

1. **UI-0** — grilla 16 px, tokens, pipeline de assets y sprites.
2. **UI-1** — barra superior, barra de acciones y panel con scroll.
3. **UI-2** — consola con pestañas y huecos para tecnología/inventario/amenaza.
4. **Slice 4A** — `Module.enabled`, R1 y guardado JSON.
5. **Slice 4B** — laboratorio + 4 tecnologías.
6. **Slice 4C** — electrólisis, condensador, reciclaje y batería.
7. **Slice 5A** — inventario genérico y catálogo de muerte.

El orden y los criterios están en [plan-ui.md](plan-ui.md), [plan-fase4.md](plan-fase4.md) y [plan-fase5.md](plan-fase5.md). No abrir un slice nuevo sin cerrar y probar el anterior.

## Mapa de documentación

| Archivo | Cuándo leerlo |
|---------|----------------|
| [diseno-juego.md](diseno-juego.md) | Qué debe hacer el juego, balance de piezas, controles |
| [plan-ui.md](plan-ui.md) | Siguiente etapa — layout, assets pixel, consola y HUD |
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
- UI: grilla de 16 px, zoom entero 1×/2×/3×, panel de 192 px, assets pixel con Genkit (RD Tile/RD+) y consola a pantalla completa. La UI va antes que las fases 4 y 5.
- HUD pendiente: hoy la barra superior muestra Cmp/E/O₂ y omite agua/comida; debe pasar a recursos letales + energía.

## Comandos habituales

```bash
make config                        # venv + dependencias desde wheelhouse/
.venv/bin/python main.py --dev     # PC, teclado como mando
python3 -m py_compile *.py         # verificar sintaxis
make dist                          # empaquetar para R36S
```

## Verificación manual útil

- 10 invernaderos con O₂=0 y comida llena → +20 O₂/d neto.
- 1 panel solar conectado → reserva de E estable o sube de día.
