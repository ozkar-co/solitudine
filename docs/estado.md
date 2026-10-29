# Estado

**Última actualización:** 2026-10-29

## Dónde estamos

| Fase | Estado |
|------|--------|
| 0–3b | **Hecho** — mapa, red, módulos, logística, supervivencia y UI base |
| 4A | **Hecho** — apagado con R1, `Module.enabled`, guardado JSON y tests |
| 4B | **Hecho** — laboratorio, 2 tecnologías y pantalla de Tecnología |
| 4C | **Hecho** — electrolizador y condensador |
| UI/balance | **Hecho** — barra de 4 vitales, modo recursos, pestañas de construcción, panel de módulo, badges de modo/pausa, créditos y balance inicial de playtest |
| Playtest | **En curso** — PC y R36S |
| 5+ | **Backlog/planificado** — chatarra/reciclador, trampa de peces, batería, agua RNG/radar, bosques/cristales, eventos y combate |

El juego es jugable en PC y en R36S. La UI (grilla de 16 px, sprites, zoom, minimapa, día/noche, lámpara) está estable.

## Próximo trabajo

1. Terminar el **playtest** de la build actual en PC y R36S.
2. Corregir bugs, legibilidad y balance.
3. Abrir el slice de **chatarra/reciclador/demolición** (ver [plan.md](plan.md)).

## Comandos

```bash
make config                        # venv + wheelhouse
make test                          # tests de regresión
.venv/bin/python main.py --dev     # PC, teclado como mando
.venv/bin/python main.py --dev --2x  # PC, ventana 2x para depurar
make dist                          # paquete PortMaster
```

## Decisiones vigentes

- Todo el código `.py` vive en la raíz; `main.py` es la única entrada.
- `module_defs.py` es la fuente única de flujos, costes y `module_active()`.
- La UI no muta la simulación; `game.py` orquesta.
- Guardado JSON automático; `save.json` está ignorado por git. `VERSION` 3; `built_day` es opcional y compatible con saves viejos.
- La luz es visual: el hábitat ilumina desde el inicio y la lámpara consume energía solo de noche, proporcional a la oscuridad.
- Un módulo apagado no produce, no consume, no da visión, no suma cap de almacén y no emite luz.
- Regla de recursos: 2 fuentes / 2 usos es una heurística, no una regla estricta. No se agrega un recurso sin un problema, una fuente y un uso definidos.
- La barra superior muestra solo los cuatro vitales; el modo recursos muestra los seis recursos.
- El menú de construcción usa pestañas por categoría y los módulos no disponibles se muestran en gris.

## Documentación

- [plan.md](plan.md) — roadmap, decisiones cerradas, matriz de recursos y próximo slice.
- [catalogo.md](catalogo.md) — módulos, categorías, tecnologías y upgrades.
- [diseno-juego.md](diseno-juego.md) — concepto, loop, sistemas, controles y UI.
- [arquitectura.md](arquitectura.md) — mapa de código y flujo.
- [assets.md](assets.md) — prompts, seeds, regeneración y créditos/easter egg.
- [joy2input.md](joy2input.md) — referencia de hardware/input en R36S.
