# Estado del proyecto

> Punto de entrada para retomar el trabajo sin contexto previo. Actualizar al cerrar una sesión relevante.

**Última actualización:** 2026-08-20

## Dónde estamos

| Fase | Estado |
|------|--------|
| 0–3b | **Hecho** — mapa, simulación, construcción, logística, buffers, depósitos finitos, UX construcción |
| 4+ | **Pendiente** — laboratorio, investigación, O₂ sostenible, eventos climáticos, desgaste, finales |

El juego es jugable en PC (`./scripts/run_dev.sh`) y en R36S vía PortMaster (`./scripts/build_dist.sh`).

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
| Balance numérico | `src/config.py` |
| Flujos/costes de módulos | `src/module_defs.py` |
| Tick produce/consume | `src/module_tick.py` |
| Conectividad (caché) | `src/network.py` → `get_connected()` |
| Construcción | `src/construction.py` |
| Bucle principal | `src/game.py` |
| Textos UI | `src/locales/es.json` |

## Decisiones recientes

- UI dividida: `ui_map.py` (mapa), `ui_panel.py` (panel), `ui.py` (HUD + modales).
- Red: BFS cacheado; invalidar al colocar cable o módulo.
- Solar: 12 E/día nominal, repartido solo en horas 6–18 (un panel cubre hábitat 8 E/d).
- Capa mapa **Recursos** (sin subtítulo “subsuelo” en UI).

## Comandos habituales

```bash
./scripts/run_dev.sh          # PC, teclado como mando
python3 -m py_compile src/*.py  # verificar sintaxis
./scripts/build_dist.sh       # empaquetar para R36S
```

## Verificación manual útil

- 10 invernaderos con O₂=0 y comida llena → +20 O₂/d neto.
- 1 panel solar conectado → reserva de E estable o sube de día.
