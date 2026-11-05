# Retroalimentación beta — TxxT

**Fecha:** 2026-11-05
**Tester:** TxxT
**Build:** beta PC 2x/1.5x (`tools/dev_beta/`)
**Estado:** registro de entrada y triage. Nada de esto está implementado todavía.

> Este archivo conserva el feedback crudo y las decisiones acordadas. Las decisiones de la trampa ya se reflejan en `plan.md`, `catalogo.md` y `diseno-juego.md`; el resto queda como triage o backlog.

## Resumen

La beta está jugable. El feedback se concentra en siete frentes:

1. **Controles y menús:** remapeo de PC, menos teclas dedicadas y menú contextual A+A por módulo.
2. **Red de cables:** nombre más claro, colocación libre, recálculo al destruir, color gris y cables sobre agua/subterráneos.
3. **UI de construcción:** scroll para muchas tarjetas y selector circular de categorías con difuminado.
4. **Balance:** comida sobrante, invernadero, extractores sin agua y trampa de peces.
5. **Mundo y generación:** depósitos extra que no cubren el mapa, anillos difusos, mundos aleatorios, mapa más grande y chunks.
6. **Créditos:** pie y borde inferior tapando el texto; el scroll no llega al final.
7. **Late game:** bichos, defensas, biodiésel, balas, eventos y fabricador Mk II.

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
- La trampa de peces figura en Soporte en el catálogo. Si se mantiene ahí, el modal de construcción pasa de 4 a 5 tarjetas y **no entra en la altura fija actual** (medido: 4 tarjetas dejan 3 px de margen; 5 desbordan ~61 px). La solución acordada es scroll, no mover la trampa por falta de espacio.

### Menú de construcción

- **Scroll vertical:** el modal debe soportar N tarjetas, no solo 4. Se van a añadir módulos y DLCs con más contenido.
- **Selector de categorías circular:** la categoría seleccionada queda centrada; las vecinas se muestran a los lados con alpha decreciente hacia los bordes; izquierda/derecha navega con wrap-around.
- Detalles abiertos: cantidad de tarjetas visibles, cantidad de etiquetas de categoría visibles, si hay animación de desplazamiento y si el scroll hace wrap en los extremos.

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
- Nota: “Soporte” y “Logística” son los candidatos más débiles. Con scroll en el modal, el espacio deja de ser criterio; la trampa de peces puede ir a Soporte o Extracción por semántica, no por capacidad.

**B30 — Créditos: pie, borde inferior y scroll**
- Feedback: “la línea del borde inferior y los controles se pintan por encima del texto y no hace scroll hasta abajo”.
- Causa confirmada: `draw_credits_modal` calcula `fixed_height` con `line_h = font_sm.get_height() + 2 = 18`, pero el paso real de las líneas es 19 (`surface.get_height() + 2`). Con 14 líneas visibles el contenido crece 14 px y el separador/pie tapa la última línea; por eso tampoco se ve el final al scrollear.
- Fix propuesto: dejar que `draw_map_modal` calcule la altura (quitar `fixed_height`) o calcularla con `_line_step` real. Añadir un test de layout que verifique que el pie no solapa la última línea.
- Estado: bug confirmado; fix simple.

**B31 — Modal de construcción con scroll**
- Feedback: debe soportar varias tarjetas y hacer scroll; se van a añadir más módulos y DLCs.
- Estado: decidido.
- Propuesta: ventana de 4 tarjetas visibles (la altura actual), scroll de 1, selección con arriba/abajo, indicador de scroll/flechas y pie fijo. Evaluar wrap en los extremos.
- Impacto: `ui.py`, `construction.BuildController` (índice/scroll), tests de navegación.

**B32 — Selector de categorías circular**
- Feedback: selector circular, difuminado hacia los bordes, con la selección actual centrada.
- Estado: decidido; detalles a definir.
- Propuesta: carrusel horizontal de 5 etiquetas; la seleccionada al centro; vecinas con alpha decreciente; izquierda/derecha cambia y mantiene el centro; wrap-around. Empezar sin animación y evaluar slide/fade después.
- Impacto: `ui.py`/`ui_modals.py`, `BuildController.menu_category` (ya hace wrap), locales y tests.

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

**B18 — Depósitos extra en el resto del mapa**
- Feedback: “no se están generando recursos en el mapa; revisar la generación de mundo”. Aclaración: no son los depósitos iniciales; el tester exploró todo el mapa y no encontró los depósitos extra/procedurales.
- Estado: **a reproducir con save nuevo**. El generador actual sí crea blobs procedurales (5.272 tiles de depósito de agua + 3.377 de mineral), pero la cobertura es muy despareja: **164 de 256 chunks de 64×64 (64%) no tienen ningún depósito**. Eso explica la sensación de mapa vacío.
- Causa probable: 45+35 blobs aleatorios de radio 3-9 sobre 1M de tiles; no hay cuota mínima por región ni control de densidad por distancia. También puede influir un save viejo que conserva un mundo generado antes de un cambio.
- Otra hipótesis: el overlay de recursos solo se dibuja en tiles visibles, no en niebla explorada. Si el tester “exploró” con radar y miró la capa de recursos, las zonas en niebla se ven vacías aunque tengan depósitos.
- Acción: reproducir con save nuevo, seed y build; confirmar si miró en niebla o en zona visible; reemplazar la dispersión aleatoria por el esquema de anillos difusos (ver propuesta) y agregar tests de cobertura.

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

### Propuesta: generación por anillos difusos

**Problema:** la generación actual tira 45 blobs de agua y 35 de mineral en posiciones uniformes sobre 1024×1024. El resultado es correcto en promedio pero muy desparejo: 64% de los chunks de 64×64 quedan vacíos y el jugador percibe el mapa como vacío al explorar. Los depósitos iniciales garantizados no alcanzan para sostener la exploración.

**Idea:** reemplazar la probabilidad uniforme por un campo de densidad radial alrededor del hábitat, con transiciones suaves (“anillos difusos”) y una cuota mínima por región.

**Modelo propuesto:**

1. **Distancia normalizada:** `d = distancia_al_hábitat / distancia_máxima`, entre 0 y 1.
2. **Perfil radial:** una función `ρ(d)` que define la densidad objetivo de depósitos por tile. Ejemplo a discutir:
   - `0.00-0.10`: solo starter patches, sin depósitos extra (protege el arranque).
   - `0.10-0.40`: densidad baja.
   - `0.40-0.70`: densidad media.
   - `0.70-1.00`: densidad alta (recompensa explorar).
   La inversa también es válida si se quiere que el centro sea rico y los bordes pobres; hay que decidirlo.
3. **Difuminado:** interpolar `ρ(d)` entre anillos con `smoothstep` y sumar ruido coherente de baja frecuencia para romper la simetría. Nada de bordes duros visibles.
4. **Muestreo por chunk:** dividir el mapa en chunks (por ejemplo 32×32 o 64×64). Para cada chunk:
   - calcular `λ = área * ρ(d_centro)`;
   - sortear `k ~ Poisson(λ)`;
   - aplicar un mínimo por chunk/anillo para evitar zonas vacías;
   - colocar `k` depósitos con jitter o blue noise para que no se apilen.
5. **Curvas separadas:** agua y mineral pueden usar perfiles distintos (por ejemplo, agua más cerca y mineral más lejos). Los starter patches se mantienen intactos.
6. **Determinismo:** todo se deriva de la seed maestra + coordenadas del chunk. La misma seed reproduce el mismo mundo.
7. **Debug:** en modo dev, un overlay de anillos/densidad y un conteo de depósitos por anillo para tunear.
8. **Tests:** cobertura mínima por anillo, densidad dentro de rango, determinismo, starter patches y no solapamiento con roca.

**Implementación por etapas:**

- **Etapa 1 (ahora, mapa 1024):** cambiar los blobs por muestreo por chunks con perfil radial; mantener arrays planos y save actual.
- **Etapa 2 (mundos aleatorios):** guardar la seed en el save y regenerar con ella; sumar UI de nueva partida/seed.
- **Etapa 3 (chunks/dinámico):** generar chunks bajo demanda con el mismo campo; guardar chunks modificados y no todo el mapa. Necesario para 2048+ y mundos infinitos.

**Decisiones abiertas:** dirección del gradiente (más recursos cerca o lejos del centro), cantidad y ancho de anillos, tamaño de chunk, cuota mínima por chunk, curvas separadas o compartidas para agua/mineral, y si los anillos se muestran al jugador o solo en debug.

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
| **Antes de la próxima beta** | B03 (verificar), B04 (bug), B05 (remapeo PC), B07 (texto laboratorio), B09 (tiempo dev), B12 (icono agua), B13 (cables grises), B16 (decisión extractor), B18 (reproducir), B30 (créditos) |
| **Slice actual: trampa + comida** | B17 (trampa), B14 (sink de comida), B15 (rebalance invernadero), B02 (solo cable sobre agua) |
| **Siguiente: UI de construcción** | B31 (scroll), B32 (selector circular), B10 (categorías) |
| **Siguiente: red y UX** | B01 (nombre), B02 (colocación libre/recálculo), B06 (menú A+A), B08 (cámara), B11 (monitoreo) |
| **Mundo** | B18 (anillos difusos), B19 (mundos aleatorios), B20 (mapa/chunks), B21 (bosques/cristales) |
| **Backlog** | B22-B29 (combate/late game) |

## Decisiones abiertas explicadas

> Cada punto tiene qué hay que decidir, el contexto, opciones y una recomendación. La recomendación no es una decisión: sirve para destrabar la conversación.

### Checklist rápido

| ID | Decisión | Opciones | Recomendación |
|----|----------|----------|---------------|
| D1 | Trampa: ventana y RNG | A nocturna / B continua / C diaria | A, 1-5 uniforme |
| D2 | Extractor sin agua | A consumo en vacío / B auto-off / C actual | B |
| D3 | Cables libres | A colocación libre / B ramificar / C radio | A |
| D4 | Teclas 3/4 | A R1/R2 / B minimapa+red / C categorías | B |
| D5 | Mapa | A 1024 / B 2048 plano / C chunks | A ahora |
| D6 | Generación | A más blobs / B anillos / C biomas | B |
| D7 | Monitoreo | A pantalla / B módulo / C híbrido | C |
| D8 | Categorías | nombres propuestos | Trampa en Extracción |
| D9 | Comida | sink + números | Biodiésel + trampas; invernadero 10 Cmp / 8 comida / 3 O₂ |
| D10 | Bosques/cristales | A scenery / B full / C split | C |
| D11 | Modal | 4 tarjetas / 5 categorías | 4/5, sin animación |

### D1 — Trampa: ventana de producción y RNG

**Qué falta decidir:** si produce solo de noche y cómo se reparte la RNG.
**Contexto:** el plan original decía 1-2 comida/noche; la decisión nueva dice ~3/día promedio. El tick actual es continuo (`dt / SECONDS_PER_DAY`), así que si se sortea por tick la varianza se diluye y la “suerte” casi no se siente; si se sortea por noche, hay que definir la ventana y el estado del panel.
**Opciones:**
- **A. Nocturna, un sorteo por noche:** 1-5 uniforme (media 3) o Poisson λ=3. Simple, legible y conserva la identidad nocturna.
- **B. Continua ponderada por oscuridad:** promedio 3/día, sin picos. Más suave y fácil de mostrar en el panel, pero menos “trampa”.
- **C. Sorteo diario al amanecer:** se calcula y se entrega durante el día. Más predecible, pero necesita almacenamiento/aviso.
**Recomendación:** A con 1-5 uniforme; si querés que existan noches de 0, usar 0-6 uniforme (media 3). Mostrar “Noche” / “En espera” en el panel.
**Para cerrar:** elegir A/B/C, rango (¿0-6 o 1-5?) y si la trampa debe estar conectada a la red para producir (el plan dice que sí).
**Impacto:** `module_tick`, `module_defs.effective_flow`, panel y tests.

### D2 — Extractor sin agua

**Qué falta decidir:** si un extractor encendido consume energía cuando no hay depósito.
**Contexto:** hoy `_job_extractor` devuelve `None` sin depósito y el test `test_depleted_extractor_does_not_consume_power` afirma consumo cero. El tester espera que consuma porque está encendido.
**Opciones:**
- **A. Consumo en vacío:** consume una fracción (p. ej. 25-50%) mientras esté encendido. Realista y castiga dejarlo prendido; puede causar apagones.
- **B. Auto-apagado:** al agotarse el depósito pasa a apagado/offline y muestra “Sin agua”. Evita energía desperdiciada; menos realista.
- **C. Consumo pleno:** consume igual que produciendo. Simple pero duro y con riesgo de softlock.
**Recomendación:** B para el próximo slice (coherente con “queda inútil”), o A con 25% y aviso claro si querés el comportamiento realista.
**Para cerrar:** elegir A/B/C; si A, fracción de consumo y si el jugador puede apagarlo a mano.
**Impacto:** `module_tick`, test, estado del panel y balance energético.

### D3 — Cables en cualquier punto

**Qué falta decidir:** qué significa “cualquier punto” y cómo se recalcula la red.
**Contexto:** hoy `_cable_preview` exige adyacencia a la red conectada o al tramo actual; no se pueden dejar tramos desconectados. El tester pide libertad y revisar el recálculo al destruir.
**Opciones:**
- **A. Colocación libre:** cualquier tile válido (suelo/agua), aunque quede desconectado; al tocar la red se conecta. Flexible para planificar; necesita distinguir visualmente conectado/desconectado.
- **B. Ramificar desde cualquier cable:** solo se permite si el nuevo cable toca otro cable; los tramos desconectados no existen. Puede ser lo que el tester ya intentó.
- **C. Libre solo cerca de la red:** un radio de tolerancia; raro y difícil de explicar.
**Recomendación:** A, con overlay de red, estado visual para cables offline e invalidación de caché en construir/demoler. Tests: un tramo desconectado no da visión ni alimenta; al conectarse, sí.
**Para cerrar:** confirmar A vs B. Si A, ¿se permite cable sobre agua? (sí, por el slice) y ¿sobre roca? (no).
**Impacto:** `construction`, `network`, `demolition`, `vision`, `ui_map` y save.

### D4 — Remapeo PC

**Qué falta decidir:** acciones de `3/4` y qué pasa con el DPAD.
**Contexto:** el mapa nuevo es 1/2 zoom, Tab construir, E aceptar, Q recursos, Esc B, J/K A/B. Hoy J/K son DPAD_LEFT/DOWN, E/Q son R1/L1 y 3/4 serían R1/R2. Además, el menú A+A elimina R1 (apagar).
**Opciones para 3/4:**
- **A. 3=R1, 4=R2:** conserva apagar y minimapa; pero apagar se va al menú A+A, así que 3 queda libre.
- **B. 3=minimapa, 4=overlay de red:** reasigna R2 y deja 3 para el futuro.
- **C. 3/4 = categoría anterior/siguiente:** útil en el menú de construcción, pero ya hay izquierda/derecha.
**DPAD:** recomiendo dejar solo flechas; J/K pasan a A/B y no se puede mantener IJKL.
**Recomendación:** 1/2 zoom, Tab construir, E aceptar, Q recursos, Esc B, J/K A/B, 3=minimapa y 4=libre para red/estación de monitoreo. Confirmar.
**Para cerrar:** elegir acción de 3 y 4; confirmar DPAD solo flechas; confirmar Enter/START y Backspace/SELECT.
**Impacto:** `dev_input`, `DEV_KEYMAP`, ayuda y tests.

### D5 — Tamaño de mapa: 2024/2048

**Qué falta decidir:** si el próximo paso es 2048 con arrays planos o chunks.
**Contexto:** hoy 1024² = ~1M tiles en listas planas. 2048² = ~4M, 4× memoria/tiempo de generación. R36S tiene memoria limitada. Chunks/dinámico es un refactor grande de `World`, save, visión, radar y cámara.
**Opciones:**
- **A. Quedarse en 1024** y hacer anillos ahora. Menor riesgo; valida el loop.
- **B. 2048 con arrays planos:** más mundo sin cambiar arquitectura; medir memoria en R36S antes.
- **C. Chunks/dinámico:** necesario para 2048+ y mundos infinitos; más trabajo y cambio de save.
**Recomendación:** A para la próxima etapa, diseñando el generador de anillos con coordenadas de chunk para no bloquear B/C. Hacer un spike de memoria de B después.
**Para cerrar:** confirmar si “2024” era 2048; si 2048 es requisito para la próxima beta o puede esperar; plataforma objetivo.
**Impacto:** `config.WORLD_SIZE`, `world`, `camera`, `savegame` y tests.

### D6 — Generación de depósitos y anillos difusos

**Qué falta decidir:** el perfil de densidad y cómo se garantiza cobertura.
**Contexto:** el generador actual crea blobs aleatorios; 64% de chunks de 64×64 quedan vacíos. El tester exploró y lo percibió vacío. La propuesta de anillos difusos está arriba.
**Opciones:**
- **A. Más blobs:** subir 45/35 a, por ejemplo, 90/70 y radios. Rápido, pero sigue sin garantizar cobertura.
- **B. Anillos + cuota por chunk:** densidad radial suave + mínimo por región. Recomendado; controla el ritmo de exploración.
- **C. Chunks/biomas con ruido:** generación más orgánica y escalable; más trabajo y requiere decidir biomas.
**Recomendación:** B en 1024 ahora; C cuando se expanda el mapa.
**Para cerrar:** dirección del gradiente (¿más lejos = más rico o al revés?), anillos y anchos, mínimo por chunk, curvas separadas para agua/mineral, y si los anillos se muestran o son invisibles.
**Impacto:** `world`, `config`, `savegame` (seed), tests y debug overlay.

### D7 — Estación de monitoreo

**Qué falta decidir:** módulo construible vs pantalla de UI.
**Contexto:** el modo recursos ya muestra cantidades, caps y tendencia global; no hay desglose por módulo ni balance de red en un solo lugar.
**Opciones:**
- **A. Pantalla de red:** acceso directo, sin tile ni energía; QoL inmediata.
- **B. Módulo:** coste, conexión y quizá energía; encaja con la progresión de base.
- **C. Híbrido:** el módulo desbloquea la pantalla; sin módulo no ves el desglose.
**Recomendación:** C si querés progresión; A si querés resolver el feedback ya. Empezar por A y convertir en C después es posible.
**Para cerrar:** elegir A/B/C; si B/C, coste, energía y tecnología.
**Impacto:** `module_defs`, UI, save y tests.

### D8 — Nombres de categorías y ubicación de la trampa

**Qué falta decidir:** nombres finales y si la trampa va en Soporte o Extracción.
**Contexto:** categorías actuales: Energía, Extracción, Soporte, Logística, Ciencia, Defensa. “Soporte” y “Logística” son ambiguos. Con scroll, el espacio ya no obliga a mover la trampa.
**Propuesta de nombres (a confirmar):** Energía, Extracción, Soporte vital, Red/Infraestructura, Investigación, Defensa.
**Trampa:** Extracción (saca comida del agua) o Soporte vital (mantiene la supervivencia). Recomiendo Extracción.
**Para cerrar:** nombres finales y categoría de la trampa.
**Impacto:** `BUILD_CATEGORIES`, locales, docs y tests. Mantener los IDs internos.

### D9 — Invernadero, trampa y sink de comida

**Qué falta decidir:** qué consume la comida y cómo se rebalancea el invernadero.
**Contexto:** hábitat −8/d; invernadero +10/d; trampa +3/d promedio. Sin sink, la comida se acumula. El invernadero actual es 8 Cmp, 1,5 d, 3 E/d, 4 agua/d → 10 comida + 2 O₂/d.
**Opciones de sink:** biodiésel (lanzallamas), fabricación de trampas, recetas del fabricador Mk II, consumo de bichos/eventos. Recomiendo biodiésel + trampas.
**Opción de invernadero:** 10 Cmp, 1,5-2 d, 8 comida/d, 3 O₂/d, 4 agua/d, 3 E/d. Ajustar después de playtest.
**Para cerrar:** elegir el primer sink y confirmar los números objetivo; si el invernadero debe seguir siendo la fuente principal o complementaria.
**Impacto:** `config`, `module_defs`, catálogo, tests y balance.

### D10 — Bosques y cristales

**Qué falta decidir:** si entran ahora y con qué uso.
**Contexto:** el plan los deja para el slice 7 hasta tener un uso concreto. El tester pide adelantarlos. La generación por anillos debe incluirlos si entran.
**Opciones:**
- **A. Solo scenery inerte:** visual/generación, sin recurso. Bajo riesgo, pero puede confundir.
- **B. Recursos completos ahora:** madera/biomasa y cristal + extractores + usos + tecnología. Mucho alcance.
- **C. Split:** bosques ahora con un uso simple (biodiésel/construcción) y cristales después con su extractor.
**Recomendación:** C si hay un uso claro para madera/biomasa; si no, A hasta definirlo.
**Para cerrar:** elegir A/B/C y el primer uso concreto de cada recurso.
**Impacto:** `world`, `config`, `module_defs`, `tech_defs`, assets, save y anillos.

### D11 — Detalles del modal y del selector

**Qué falta decidir:** cuántas tarjetas/etiquetas se ven y si hay animación.
**Contexto:** B31/B32 ya están decididos en dirección.
**Propuesta:** 4 tarjetas visibles, scroll de 1, wrap opcional; carrusel de 5 categorías, alpha decreciente, wrap, sin animación al principio.
**Para cerrar:** confirmar 4/5, si querés animación y si el scroll debe hacer wrap.
**Impacto:** `ui.py`, `ui_modals.py`, `BuildController` y tests.

## Siguiente etapa propuesta

> Secuencia sugerida para destrabar la beta y después seguir con el slice. No es una decisión cerrada; se puede reordenar.

| Etapa | Contenido | Por qué |
|-------|-----------|---------|
| **0. Quick fixes beta** | B03 (verificar), B04/B05 (remapeo), B07 (copy), B12 (gota), B13 (cables grises), B30 (créditos), B09 (tiempo dev) | Son cambios acotados que mejoran la próxima build sin tocar el loop. |
| **1. Mundo** | B18 (reproducir), anillos difusos, B19 (seed aleatoria), B20 (medir 2048), tests de cobertura | Es el problema más visible del tester y condiciona exploración/balance. |
| **2. UI de construcción** | B31 (scroll), B32 (selector circular), B10 (nombres) | Desbloquea agregar módulos y DLCs sin romper el modal. |
| **3. Trampa + comida** | B17, D1 (RNG/noche), D9 (sink/invernadero), B16 (decisión extractor) | Cierra el slice actual y el problema de comida. |
| **4. Red y módulos** | B01 (nombre), B02 (cables libres), B06 (menú A+A), B08 (cámara), B11 (monitoreo) | Mejora la UX de la red y prepara más módulos. |
| **5. Contenido/late game** | B21 (bosques/cristales), B22-B29 (combate, biodiésel, eventos) | Requiere sistemas nuevos; no antes de estabilizar lo anterior. |

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
