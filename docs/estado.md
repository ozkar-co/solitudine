# Estado

**Última actualización:** 2026-10-28

## Dónde estamos

| Fase | Estado |
|------|--------|
| 0–3b | **Hecho** — mapa, red, módulos, logística, supervivencia y UI base |
| 4A | **Hecho** — apagado con R1, `Module.enabled`, guardado JSON y tests |
| 4B | **Siguiente** — laboratorio, 2 tecnologías y pantalla de Tecnología mínima |
| 4C | **Pendiente** — electrolizador y condensador |
| 5+ | **Backlog** — alimañas, inventario, combate, eventos, finales |

El juego es jugable en PC y en R36S. La UI (grilla de 16 px, sprites, zoom, minimapa, día/noche, lámpara) ya está estable.

## Próximo trabajo

1. **4B** — ver [plan.md](plan.md).
2. **4C** — ver [plan.md](plan.md).
3. **Playtest corto** antes de abrir cualquier backlog.

## Comandos

```bash
make config                        # venv + wheelhouse
make test                          # tests de regresión
.venv/bin/python main.py --dev     # PC, teclado como mando
make dist                          # paquete PortMaster
```

## Decisiones vigentes

- Todo el código `.py` vive en la raíz; `main.py` es la única entrada.
- `module_defs.py` es la fuente única de flujos, costes y `module_active()`.
- La UI no muta la simulación; `game.py` orquesta.
- Guardado JSON automático; `save.json` está ignorado por git.
- La luz es visual: el hábitat ilumina desde el inicio y la lámpara consume energía solo de noche, proporcional a la oscuridad.
- Un módulo apagado no produce, no consume, no da visión, no suma cap de almacén y no emite luz.
- Regla de recursos: no agregar uno nuevo hasta que los seis actuales tengan dos fuentes y dos usos.

## Documentación

- [plan.md](plan.md) — roadmap y alcance del próximo slice.
- [diseno-juego.md](diseno-juego.md) — concepto, loop, sistemas y controles.
- [arquitectura.md](arquitectura.md) — mapa de código y flujo.
- [assets.md](assets.md) — prompts, seeds y regeneración.
- [joy2input.md](joy2input.md) — referencia de hardware/input en R36S.
