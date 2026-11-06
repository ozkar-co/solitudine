# Estado

**Última actualización:** 2026-11-06

## Dónde estamos

| Fase | Estado |
|------|--------|
| 0–3b | **Hecho** — mapa, red, módulos, logística, supervivencia y UI base |
| 4A | **Hecho** — apagado con R1, `Module.enabled`, guardado JSON y tests |
| 4B | **Hecho** — laboratorio, 2 tecnologías y pantalla de Tecnología |
| 4C | **Hecho** — electrolizador y condensador |
| UI/balance | **Hecho** — barra de 4 vitales, modo recursos, pestañas de construcción, panel de módulo, badges de modo/pausa, créditos y balance inicial de playtest |
| Playtest | **Hecho** — PC y R36S; ajustes aplicados |
| Fundación recursos/costes | **Hecho** — pool único, `Cost` multi-material, `cost_paid` y save v4 |
| Chatarra/reciclador/demolición | **Hecho** — ruinas, recogida, reciclador, demolición y cancelación |
| Beta etapa 0 | **Hecho** — remapeo PC, tiempo dev, copy del laboratorio, créditos/layout, icono de agua, cables grises |
| Beta etapa 1 | **Hecho** — mundo parametrizable 2048, arrays compactos, save size/seed, anillos difusos, bosques/carbón/cristales y recursos nuevos |
| Beta etapa 2 | **Hecho** — scroll del menú, carrusel animado de categorías y nombres nuevos |
| Beta etapa 3 | **Hecho** — trampa de peces, RNG nocturna, extractor/mina al 50%, invernadero 6/3 y procesador de biodiésel como sink |
| Beta etapa 4 | **Hecho** — cables libres, menú A+A, cámara a bordes, monitoreo y rename Cable→Enlace |
| Fase 5 | **Hecho** — generador multi-combustible, solar/carbón/cristal/almacenamiento, batería |
| v6 | **Siguiente** — cristales, tanques especializados, combate/eventos y prerequisitos tecnológicos |

El juego es jugable en PC y en R36S. La UI (grilla de 16 px, sprites, zoom, minimapa, día/noche, lámpara) está estable. El loop de chatarra (ruinas → reciclador → mineral) y la demolición ya funcionan.

## Próximo trabajo

**Roadmap actual (plan.md):**

1. **v6 — cristales:** usos avanzados (láseres/tecnología), todavía sin contenido de combate.
2. **v6 — almacenamiento especializado:** tanque de O₂ con investigación propia y tanques de agua/mineral.
3. **v6 — árbol tecnológico:** prerequisitos y tecnologías que solo desbloquean otras tecnologías; después combate/eventos.

**Estado beta:** etapas 0-4 y fase 5 implementadas (95 tests). Detalle en [beta-txxt.md](beta-txxt.md).

## Comandos

```bash
make config                        # venv + wheelhouse
make test                          # tests de regresión
.venv/bin/python main.py --dev     # PC, teclado como mando
.venv/bin/python main.py --dev --2x  # PC, ventana 2x para depurar
.venv/bin/python main.py --dev --seed ABC-123  # mundo reproducible
.venv/bin/python main.py --dev --world-size 1024  # mapa más chico para probar
make dist                          # paquete PortMaster
./tools/dev_beta/build.sh          # beta PC Linux 1x (temporal)
tools\dev_beta\build.ps1           # beta PC Windows 1x (PowerShell)
```

## Decisiones vigentes

- Todo el código `.py` del juego vive en la raíz; `main.py` es la entrada. `tools/dev_beta/` es una entrada temporal de beta PC, aislada del juego.
- `module_defs.py` es la fuente única de flujos, costes y `module_active()`.
- Recursos y costes: pool único (`ResourcePool`) y `Cost` multi-material; `Stockpile` ya no existe.
- Chatarra: cap 30 (+40 por almacén general), ruinas seleccionadas y recogidas con A; demolición/cancelación con B y confirmación A.
- La UI no muta la simulación; `game.py` orquesta.
- Guardado JSON automático; `save.json` está ignorado por git. `VERSION` 4, sin migración: los saves anteriores se borran al cargar. Se guardan recursos, stats, `cost_paid`, `fuel_resource`, ruinas, `size` y `seed`.
- La luz es visual: el hábitat ilumina desde el inicio y la lámpara consume energía solo de noche, proporcional a la oscuridad.
- Un módulo apagado no produce, no consume, no da visión, no suma cap de almacén y no emite luz.
- Regla de recursos: 2 fuentes / 2 usos es una heurística, no una regla estricta. Madera y carbón alimentan el generador; el biodiésel se usa en generador y Cristalografía; los cristales quedan para v6.
- La barra superior muestra solo los cuatro vitales; el modo recursos muestra los once recursos.
- Fuente UI: Pixel Operator 16/24 (cuerpo regular, títulos bold); VT323 queda como fallback/A-B.
- El menú de construcción usa scroll vertical animado, carrusel circular de categorías y tarjetas horizontales por módulo; la seleccionada se resalta en ámbar y las no disponibles se muestran en gris.
- Cables de colocación libre; los tramos desconectados no alimentan hasta conectar. El display del cable es **Enlace**.
- A+A abre un menú declarativo desde `ModuleDef.menu_actions`, con acciones comunes generadas y un registro central de handlers. B ya no demuele módulos; queda para cables.
- La cámara llega a los bordes del mapa; el cursor sigue limitado a lo explorado.
- Cada partida nueva usa una **seed aleatoria con formato `ABC-123`** (3 letras + 3 números); `--seed`/`SOLITUDINE_SEED` permite reproducir un mundo. El save conserva `size` y `seed`. La seed se muestra como nombre del planeta arriba a la izquierda (`SOLITUDINE ABC-123`). La pausa ofrece **Nueva partida** con confirmación y **Salir**.
- La estación de monitoreo requiere estar online y conectada para abrir la pantalla de red, con producción y consumo en dos columnas.
- Todos los modales usan `ui_modals.draw_modal` (título/subtítulo/columnas/scroll/ayuda) y son anchos; no se redefinen cajas ni pies.
- Beta PC pública 1x (`main.py`/`SolitudineBeta`); `--2x` queda para desarrollo local y no hay variante intermedia.
- **Generador eléctrico:** empieza apagado y sin combustible; consume 1 unidad/día y produce 5/12/20 E/d con madera/carbón/biodiésel. Sin combustible seleccionado o disponible se apaga solo.
- **Solar y carbón:** exigen Fotovoltaica (3 Cmp, 0,5 d) y Minería de carbón (4 Cmp, 0,75 d). **Cristalografía** cuesta 10 Cmp + 8 biodiésel y 3 d; **Almacenamiento especializado** cuesta 6 Cmp + 2 mineral y 2 d.
- **Almacén general:** +40 a recursos generales, sin energía ni O₂. **Batería:** +100 cap de energía.
- **v6:** tanque de O₂ con investigación propia, tanques especializados, usos de cristales, prerequisitos y tecnologías que solo desbloquean otras tecnologías.

## Documentación

- [plan.md](plan.md) — roadmap, decisiones cerradas, matriz de recursos y próximo slice.
- [catalogo.md](catalogo.md) — módulos, categorías, tecnologías y upgrades.
- [diseno-juego.md](diseno-juego.md) — concepto, loop, sistemas, controles y UI.
- [arquitectura.md](arquitectura.md) — mapa de código y flujo.
- [assets.md](assets.md) — prompts, seeds, regeneración y créditos/easter egg.
- [beta-txxt.md](beta-txxt.md) — retroalimentación beta de TxxT (entrada y triage).
- [joy2input.md](joy2input.md) — referencia de hardware/input en R36S.
