# Retroalimentación beta — TxxT

**Fecha:** 2026-11-05
**Tester:** TxxT
**Build:** beta PC 2x/1.5x (`tools/dev_beta/`)
**Estado:** registro de entrada y triage. Nada de esto está implementado todavía.

> Este archivo conserva el feedback crudo y las decisiones acordadas. Las decisiones de la trampa ya se reflejan en `plan.md`, `catalogo.md` y `diseno-juego.md`; el resto queda como triage o backlog.

## Resumen

La beta está jugable. El feedback se concentra en cinco frentes:

1. **Controles y menús:** remapeo de PC, menos teclas dedicadas y menú contextual A+A por módulo.
2. **Red de cables:** nombre más claro, colocación libre, recálculo al destruir, color gris y cables sobre agua/subterráneos.
3. **Balance:** comida sobrante, invernadero, extractores sin agua y trampa de peces.
4. **Mundo:** recursos que no aparecen, mundos aleatorios, mapa más grande, chunks, bosques y cristales.
5. **Late game:** bichos, defensas, biodiésel, balas, eventos y fabricador Mk II.

## Decisiones generales acordadas

### Trampa de peces

Reemplazan los valores provisionales de `plan.md` (1-2 Cmp, 1-2 comida/noche):

- **Coste:** 2 Cmp.
- **Obra:** 0,5 día.
- **Energía:** no consume.
- **Producción:** comida de forma aleatoria (RNG), con **promedio de 3 por día**.
- **Agua:** se coloca sobre agua y el cable puede ir sobre agua; se detiene si el agua se agota.
- **Demolición:** no deja ruina. Se destruye directamente y devuelve chatarra.
- **Pendiente de definir:**
  - Si la producción sigue restringida a la noche o pasa a ser diaria.
  - La distribución RNG (por ejemplo, 1-5 uniforme con media 3; a probar).
  - El monto de chatarra directa (la fórmula general es 0,6-0,9 del equivalente mineral, con cap de red).

### Categorías del menú de construcción

- Se acepta revisar y renombrar las categorías ahora.
- Nombres finales y mapping de módulos: **a definir**.
- Categorías actuales: Energía, Extracción, Soporte, Logística, Ciencia, Defensa.
- La trampa de peces figura en Soporte en el catálogo. Si se mantiene ahí, el modal de construcción pasa de 4 a 5 tarjetas y **no entra en la altura fija actual** (medido: 4 tarjetas dejan 3 px de margen; 5 desbordan ~61 px). Opciones: mover la trampa a Extracción, agregar scroll/ventana al modal o redimensionar las tarjetas.

### Controles PC (beta)

Nuevo mapa para la beta de PC, reemplazando el esquema actual `Z/X/C/V` + `IJKL`:

| Acción | Tecla |
|--------|-------|
| Aceptar / confirmar | `E` |
| B / volver / cancelar | `Esc` |
| Menú de construcción | `Tab` |
| Recursos (capa) | `Q` |
| Zoom in | `1` |
| Zoom out | `2` |
| Otros botones L/R que no son zoom | `3` y `4` |
| Duplicado de A | `J` |
| Duplicado de B | `K` |

Notas de implementación:

- Hoy `1` está mapeado a `L2` y `2` a `R2`; el zoom real usa `L1/L2` y `R2` abre el minimapa. Por eso los atajos actuales no coinciden.
- `J` y `K` hoy son `DPAD_LEFT` y `DPAD_DOWN`. Al pasar a A/B, el DPAD de teclado debe quedar en las flechas o reasignarse.
- `3`/`4` corresponden a `R1`/`R2` en el esquema actual (`R1` apaga/enciende, `R2` minimapa). Si se elimina `R1` por el menú contextual, la acción final de `3` queda a definir.
- `E` y `Q` hoy son `R1` y `L1`; el remapeo mueve esas acciones a `3/4` y al zoom.
- Actualizar también `DEV_KEYMAP`, los hints y la ayuda contextual.

### Acciones de módulos

- **Decisión de dirección:** no usar teclas dedicadas para destruir o apagar. Todas las acciones van en un **menú contextual del módulo**:
  - A selecciona el módulo.
  - A otra vez abre el menú del módulo.
  - Desde ahí se apaga/enciende, se demuele, se investiga (laboratorio) o se ejecuta la acción especial.
- Impacto: desaparecen los atajos directos `B` (demolición) y `R1` (apagado); hay que actualizar `game_input.py`, los hints, los tests y el panel.
- El laboratorio debe decir **“Pulsa A para investigar”**, no “menú de investigación”.

## Feedback por tema

### 1. Controles, menús y UI

**B01 — Renombrar “Cable”**
- Feedback: “cambiar el nombre de cable por algo más obvio”.
- Estado: abierto.
- Candidatos: Enlace, Conexión, Conector.
- Nota técnica: cambiar solo el texto visible; conservar el ID `cable` para no romper saves. Actualizar `locales/es.json`, `catalogo.md`, `diseno-juego.md` y el prompt del sprite.

**B02 — Cables en cualquier punto y reglas de red**
- Feedback: “que se puedan poner cables en cualquier punto, validar las reglas de ‘red’ porque con destruir ya toca volver a calcular eso cada vez”.
- Interpretación: permitir colocar cable sin exigir adyacencia a la red (tramos desconectados), y revisar el recálculo de conectividad al construir/demoler.
- Estado: abierto; confirmar si “cualquier punto” significa cable libre o ramificar desde cualquier cable.
- Impacto: `construction._cable_preview` (`NO_NETWORK`/`CABLE_NOT_CHAIN`), `network.compute_connected`, invalidación de caché en `demolition.py` y `construction.refresh_network`.
- Riesgo: más cables desconectados en el mapa; validar rendimiento y que la red solo considere lo alcanzable desde el hábitat.

**B03 — Almacén apagable**
- Feedback: “apagar el almacén no tiene sentido, no se debería poder apagar (revisar, es de una versión anterior)”.
- Estado: **ya corregido en `master`**. `module_def(STORAGE).can_toggle=False` y el test `test_storage_cannot_be_disabled` lo cubren.
- Acción: verificar que la build entregada al tester incluya la corrección; si no, es un problema de versión.

**B04 — Atajos R2/L2 del menú de debug**
- Feedback: “los atajos de R2 y L2 en el menú de debug no coinciden”.
- Evidencia: `dev_input.py` mapea `1 -> L2` y `2 -> R2`; `game.py` usa `L1/L2` para zoom y `R2` para minimapa. `DEV_KEYMAP` muestra `1/2=L2/R2`, que no coincide con las acciones reales.
- Estado: bug confirmado; se resuelve con el remapeo B05.

**B05 — Remapeo de PC**
- Feedback: ver tabla de “Controles PC (beta)”.
- Estado: decidido; pendiente de implementar.
- Archivos: `dev_input.py`, `game_input.py`, `game.py`, `game_help.py`, `ui_input.py`, `locales/es.json`, tests de input.

**B06 — Menú A+A por módulo**
- Feedback: “para destruir y apagar no una tecla dedicada sino desde el menú de A de cada módulo; todos los módulos tienen menú con A+A (seleccionar y abrir menú)”.
- Estado: decidido como dirección; falta diseño de UI.
- Impacto: quitar `R1` y `B` como atajos directos, agregar menú contextual, adaptar panel/hints/tests. `B` sigue siendo “volver/cancelar” en modales.
- Nota: el laboratorio ya usa A+A para abrir Tecnología; el patrón se generaliza.

**B07 — Texto del laboratorio**
- Feedback: “en el laboratorio que diga ‘pulsa A para investigar’, porque ‘menú de investigación’”.
- Estado: abierto; cambio de copy.
- Archivos: `locales/es.json` (`action.research`, `panel.action_hint`) y `ui_panel.py`.

**B08 — Cámara hasta el límite del mapa**
- Feedback: “la cámara no llega hasta el límite del mapa; hacerlo dinámico, el mapa puede crecer en el futuro”.
- Evidencia: `World.camera_bounds()` limita al área explorada + margen; `camera.visible_tiles()` y varios defaults usan `WORLD_SIZE`.
- Estado: abierto. Definir si el límite es el mapa completo o el área explorada.
- Impacto: `camera.py`, `world.py`, `game.py`; al crecer el mapa, `visible_tiles`/`clamp_cursor` deben usar `world.size`, no la constante.

**B09 — Acelerar tiempo en modo dev**
- Feedback: “en modo dev (testing) un botón que acelere el tiempo para llegar a bugs de late game”.
- Estado: abierto; tecla/multiplicador a definir.
- Impacto: `game.py`/`simulation.py`; solo `--dev`, sin afectar saves ni la build normal. Útil para probar día 25, RNG, consumo y eventos.

**B10 — Renombrar categorías**
- Feedback: “las categorías necesitan un cambio de nombre; podemos hacerlo de una vez, revisar los nombres”.
- Estado: abierto; nombres finales a definir.
- Nota: “Soporte” y “Logística” son los candidatos más débiles. Revisar también si la trampa de peces va en Soporte o Extracción.

### 2. Módulos y red

**B11 — Estación de monitoreo**
- Feedback: “crear un módulo ‘estación de monitoreo’ o similar para ver cuánto consume y produce toda la red”.
- Estado: idea; decidir si es módulo o pantalla de UI.
- Nota: una pantalla de red no ocupa tile ni consume energía y muestra los mismos datos; un módulo agrega coste, conexión y presencia en el mapa. Si es módulo, definir coste, energía, desbloqueo y si necesita estar online.
- Datos: consumo/producción por recurso, balance neto, módulos activos/offline, caps y cuellos de botella.

**B12 — Icono de agua**
- Feedback: “el icono de agua que sea una gotica”.
- Estado: abierto; regenerar `assets/icons/water.png` y actualizar `docs/assets.md` (prompt/seed).
- Nota: verificar que siga legible a 16×16 y en la barra superior/modo recursos.

**B13 — Cables grises**
- Feedback: “que los cables sean grises y no amarillos (incluye actualizar el sprite)”.
- Estado: abierto.
- Evidencia: `COL_CABLE = (255, 230, 80)` y `assets/icons/cable.png` es amarillo.
- Impacto: `ui_theme.COL_CABLE` se usa también para la barra de obra y el borde de selección (`ui_map.py:96` y `:235`). Separar `COL_CABLE` de `COL_BUILD_BAR`/`COL_SELECT` antes de cambiar el color.
- Assets: regenerar `cable.png` en gris y actualizar `docs/assets.md`.

### 3. Balance y recursos

**B14 — Consumir comida**
- Feedback: “pensar en una forma de consumir comida; se produce demasiada y no se gasta”.
- Estado: abierto; es un problema de diseño de recursos.
- Usos candidatos: biodiésel (lanzallamas), fabricación de trampas, fabricador Mk II con recetas, eventos/consumo de bichos.
- Nota: hoy el hábitat consume 8 comida/d y el invernadero produce 10/d; con la trampa (~3/d promedio) el excedente crece. Definir el sink antes de subir la producción.

**B15 — Rebalancear invernadero**
- Feedback: “más caro, menos comida, un poquito más de oxígeno; así se complementa con la trampa de peces”.
- Estado: abierto; números a definir después de fijar la RNG de la trampa.
- Actual: 8 Cmp, 1,5 d, 3 E/d, 4 agua/d → 10 comida/d + 2 O₂/d.
- Dirección: coste ↑, comida ↓, O₂ ↑. Mantener el consumo de agua/energía coherente.

**B16 — Extractores sin agua**
- Feedback: “revisar los extractores de agua sin agua; deberían consumir por estar encendidos”.
- Estado: **conflicto con el comportamiento actual**. `module_tick._job_extractor` no crea job si no hay depósito; el test `test_depleted_extractor_does_not_consume_power` afirma que no consume.
- Opciones: (a) consumir en vacío mientras esté encendido, (b) apagarlo automáticamente al agotarse, (c) mantener el comportamiento actual.
- Si se acepta (a): actualizar test, panel/estado, balance y el texto de la UI.

**B17 — Trampa de peces**
- Feedback: ver “Decisiones generales”.
- Estado: decidido; pendiente de implementar en el slice actual.
- Requisitos: placement sobre agua, cable sobre agua, sin energía, 2 Cmp, 0,5 d, RNG ~3 comida/día, parada al agotarse el agua, sin ruina y chatarra directa.
- Abierto: noche vs día, distribución RNG y fórmula exacta de chatarra.

### 4. Mundo y cámara

**B18 — Recursos que no se generan**
- Feedback: “no se están generando recursos en el mapa; revisar la generación de mundo”.
- Estado: **a reproducir**. Verificación rápida del seed actual `NEP325`: el generador produce 12.521 tiles de agua, 5.272 tiles con depósito de agua y 3.377 con mineral.
- Hipótesis: problema de exploración/niebla en la partida del tester, expectativa de recursos renovables, o un bug específico de la build/save. Pedir seed, save y zona explorada.
- Acción: reproducir con la build beta y confirmar si “no se generan” significa “no aparecen cerca” o “no se regeneran”.

**B19 — Mundos aleatorios**
- Feedback: “ya podemos habilitar los mundos aleatorios”.
- Estado: abierto; requiere diseño.
- Nota técnica: hoy `WORLD_SEED` es fijo y `load_game()` llama `generate_world()` sin seed. Para mundos aleatorios hay que guardar la seed en el save y regenerar con ella; implica cambio de formato/versión.
- Decidir: seed visible, reroll, mundos compartidos por seed, y compatibilidad con saves v4.

**B20 — Mapa más grande, chunks y generación dinámica**
- Feedback: “expandir a 2024” (probablemente 2048), “considerar sistema de chunks y generación dinámica”.
- Estado: abierto; cambio de arquitectura.
- Contexto: hoy `WORLD_SIZE=1024` y el mundo son listas planas de ~1M de tiles; 2048 serían ~4M. Chunks/dinámico cambia generación, visión, save, cámara, radar y depósitos.
- Acción: confirmar tamaño objetivo y si se hace antes o después de estabilizar el loop.

**B21 — Bosques y cristales**
- Feedback: “metamos de una vez bosques y cristales”.
- Estado: abierto; el plan actual los deja para el slice 7 y pide un uso concreto por recurso.
- Nota: bosques renovables (brotes/regrow, bloquean construcción) y cristales finitos bajo tierra; requieren recursos, extractor, usos y probablemente cambios de generación/save.

### 5. Ideas adicionales (backlog)

Estas ideas dependen de combate/late game y no entran en el slice actual:

- **B22 — Lanzallamas y minas terrestres** para cuando existan bichos.
- **B23 — Biodiésel como combustible** de lanzallamas, producido con mucha comida. Es un sink de comida.
- **B24 — Torretas con balas**, un recurso nuevo. Definir fuente, uso y si cumple la regla de recursos.
- **B25 — Bichos que destruyen el radar y comen cable** hasta que el jugador corte un tramo y el cable quede desconectado, o hasta acabar con todo. Requiere pathing/enemigos y conectividad de red.
- **B26 — Cables subterráneos** para evitar bichos. Nueva variante de cable: coste, render, save y reglas de red.
- **B27 — La luz atrae bichos**. Interacción luz/enemigos; revisar lámpara, hábitat y noche.
- **B28 — Fabricador Mk II con recetas**: elegir qué produce y convertir minerales en distintos materiales (a definir). Requiere sistema de recetas y nuevos materiales.
- **B29 — Eventos aleatorios desde el día 25** que puedan destruir módulos. Requiere sistema de eventos, probabilidades, avisos y guardado.

## Triage propuesto

> Propuesta de orden; no es una decisión cerrada.

| Bucket | Items |
|--------|-------|
| **Antes de la próxima beta** | B03 (verificar), B04 (bug), B05 (remapeo PC), B07 (texto laboratorio), B09 (tiempo dev), B12 (icono agua), B13 (cables grises), B16 (decisión extractor), B18 (reproducir recursos) |
| **Slice actual: trampa + comida** | B17 (trampa), B14 (sink de comida), B15 (rebalance invernadero), B02 (solo cable sobre agua) |
| **Siguiente: red y UX** | B01 (nombre), B02 (colocación libre/recálculo), B06 (menú A+A), B08 (cámara), B10 (categorías), B11 (monitoreo) |
| **Mundo** | B19 (mundos aleatorios), B20 (mapa/chunks), B21 (bosques/cristales) |
| **Backlog** | B22-B29 (combate/late game) |

## Conflictos y preguntas abiertas

1. **Trampa 3/día vs producción nocturna.** El plan original decía 1-2 comida/noche; la decisión nueva dice ~3/día promedio. ¿Sigue siendo solo de noche? ¿La RNG se sortea por noche o por tick?
2. **Extractor en vacío.** B16 contradice el test actual. ¿Consume, se auto-apaga o se mantiene?
3. **Cables libres.** B02 puede eliminar `NO_NETWORK`/`CABLE_NOT_CHAIN`. ¿Se permite construir redes desconectadas y conectarlas después? ¿Cómo se valida el recálculo al demoler?
4. **Remapeo PC.** `J/K` como A/B choca con `IJKL` de DPAD. ¿El DPAD queda solo en flechas? ¿Qué acciones van en `3/4` si `R1` desaparece?
5. **Mapa 2024/2048.** Confirmar el número; si es 2048, evaluar memoria y si chunks entra en esta fase.
6. **Recursos no generados.** El generador actual sí produce; falta reproducir el caso del tester.
7. **Estación de monitoreo.** ¿Módulo construible o pantalla de red?
8. **Categorías.** Nombres finales y ubicación de la trampa (Soporte vs Extracción).
9. **Invernadero/trampa.** Números finales después de definir la RNG de la trampa y el sink de comida.
10. **Bosques/cristales.** El plan los difiere hasta tener usos concretos; el tester pide adelantarlos. ¿Se abre el alcance?

## Archivos probablemente afectados

| Área | Archivos |
|------|----------|
| Input/controles | `dev_input.py`, `game_input.py`, `game.py`, `ui_input.py`, `game_help.py`, `locales/es.json` |
| Red/cables | `construction.py`, `network.py`, `demolition.py`, `ui_map.py`, `ui_theme.py` |
| Módulos/UI | `module_kind.py`, `module_defs.py`, `config.py`, `ui.py`, `ui_panel.py`, `locales/es.json` |
| Mundo/cámara | `world.py`, `config.py`, `camera.py`, `savegame.py` |
| Assets | `assets/icons/water.png`, `assets/icons/cable.png`, `docs/assets.md` |
| Tests | `test_sim.py` (input, red, extractor, trampa, save) |

## Referencias

- [plan.md](plan.md) — roadmap y decisiones cerradas.
- [catalogo.md](catalogo.md) — módulos, categorías y números.
- [diseno-juego.md](diseno-juego.md) — loop, sistemas y controles.
- [assets.md](assets.md) — sprites, prompts y seeds.
- [estado.md](estado.md) — estado actual y próximos pasos.
