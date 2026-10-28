# Estado del proyecto

> Punto de entrada para retomar el trabajo sin contexto previo. Actualizar al cerrar una sesión relevante.

**Última actualización:** 2026-10-28

## Dónde estamos

| Fase | Estado |
|------|--------|
| 0–3b | **Hecho** — mapa, simulación, construcción, logística, buffers, depósitos finitos, UX construcción |
| 4+ | **Pendiente** — laboratorio, investigación, O₂ sostenible, eventos climáticos, desgaste, finales |

El código está aplanado en la raíz (sin `src/`). El juego es jugable en PC (`make config` + `.venv/bin/python main.py --dev`) y en R36S vía PortMaster (`make dist`).

## Próximo trabajo sugerido

1. **Laboratorio + investigación** — O₂ sostenible (hoy solo reserva inicial + invernadero +2/d).
2. **Eventos globales** — heladas, calor, tormentas (diseño en `diseno-juego.md` § eventos).
3. **Desgaste / estados degradados** — enum existe; falta simulación real.

## Mapa de documentación

| Archivo | Cuándo leerlo |
|---------|----------------|
| [diseno-juego.md](diseno-juego.md) | Qué debe hacer el juego, balance de piezas, controles |
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
