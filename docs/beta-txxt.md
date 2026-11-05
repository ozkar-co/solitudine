# Retroalimentación beta — TxxT

**Fecha:** 2026-11-05
**Tester:** TxxT
**Build:** beta PC 2x/1.5x (`tools/dev_beta/`)
**Estado:** etapas 0-3 implementadas (2026-11-05); etapa 4 en triage.

> Este archivo conserva el feedback crudo y las decisiones acordadas. La tabla de implementación de abajo es el estado real; las secciones de feedback conservan el texto original.

## Implementación (2026-11-05)

| Etapa | Implementado | Pendiente |
|-------|--------------|-----------|
| 0 | B04/B05 (remapeo PC), B07 (copy), B09 (tiempo dev), B12 (gota), B13 (cables grises), B30 (créditos/layout), créditos TxxT/JuanDi | Verificar B03 en la próxima build |
| 1 | D5 (2048 parametrizable, arrays, save size/seed), D6 (anillos, bosques/carbón/cristales), D10, B19 (seed) | B18 reproducir el caso del tester; benchmark R36S |
| 2 | B31 (scroll), B32 (carrusel animado), D8 (nombres), D11 (animaciones) | Ajustes de tuning visual |
| 3 | B17/D1 (trampa RNG nocturna), B16/D2 (extractor/mina 50%), B15/D9 (invernadero 6/3), sink de comida (biodiésel) | B14: más usos para la comida |
| 4 | — | B01, B02, B06, B08, B11 (red, A+A, cámara, monitoreo, rename) |

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
- **Producción:** solo de noche, **una tirada por hora**, incluyendo 0, con **promedio de 3 por noche**. Propuesta: ventana 20:00–04:00 (8 tiradas), 50% de 0 y si no uniforme 0–1,5 (media 0,375/hora).
- **Agua:** se coloca sobre agua y el cable puede ir sobre agua; se detiene si el agua se agota.
- **Demolición:** no deja ruina. Se destruye directamente y devuelve chatarra.
- **Pendiente de definir:**
  - Afinar la distribución y la ventana nocturna exacta.
  - El monto de chatarra directa (la fórmula general es 0,6-0,9 del equivalente mineral, con cap de red).

### Categorías del menú de construcción

- **Nombres finales:** Energía, Extracción, Soporte Vital, Red Logística, Investigación, Defensa.
- **Trampa de peces:** Extracción.
- El modal de construcción pasa a scroll vertical para N tarjetas; el espacio deja de ser una restricción. El selector de categorías es circular, con la selección centrada y etiquetas difuminadas hacia los bordes.

### Menú de construcción

- **Scroll vertical:** el modal debe soportar N tarjetas, no solo 4. Se van a añadir módulos y DLCs con más contenido.
- **Selector de categorías circular:** la categoría seleccionada queda centrada; las vecinas se muestran a los lados con alpha decreciente hacia los bordes; izquierda/derecha navega con wrap-around.
- **Animaciones decididas:** scroll animado y carrusel con slide/fade desde ya. Punto de partida: 4 tarjetas visibles y 5 etiquetas. Pendiente: si hace wrap en los extremos y duración de la animación.

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
| Otros botones L/R que no son zoom | `3` (minimapa) y `4` (apagar/encender temporal) |
| Duplicado de A | `J` |
| Duplicado de B | `K` |

Notas de implementación (2026-11-05):

- `1`/`2` = `L1`/`L2` (zoom in/out); `3` = `R2` (minimapa); `4` = `R1` (apagar/encender temporal, hasta el menú A+A de la etapa 4).
- `J`/`K` = A/B; se elimina el DPAD de teclado: WASD mueve el cursor y las flechas mueven la cámara.
- `E` = A; `Q` = X (recursos); `Tab` = Y (construir); `Esc` = B.
- `T` acelera el tiempo en modo dev.
- `DEV_KEYMAP`, los hints y la ayuda contextual están actualizados.

### Acciones de módulos

- **Decisión de dirección:** no usar teclas dedicadas para destruir o apagar. Todas las acciones van en un **menú contextual del módulo**:
  - A selecciona el módulo.
  - A otra vez abre el menú del módulo.
  - Desde ahí se apaga/enciende, se demuele, se investiga (laboratorio) o se ejecuta la acción especial.
- Impacto: desaparecen los atajos directos `B` (demolición) y `R1` (apagado); hay que actualizar `game_input.py`, los hints, los tests y el panel.
- El laboratorio debe decir **“Pulsa A para investigar”**, no “menú de investigación”.

### Créditos

- **TxxT:** beta testing, bugcatcher y aporte de ideas. Agregar sección **BETA TESTING** propia con ese rol (o moverlo al equipo, si se prefiere).
- **JuanDi (Juandi Alfa):** alpha y beta testing; colaboración creativa y aporte de ideas.
- Actualizar `credits.py` y `locales/es.json`; revisar que el scroll de créditos siga funcionando con una sección más (ver B30).

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
- Estado: **decidido (D3)**: colocación libre, con cables desconectados marcados y recálculo al conectar/demoler.
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
- Estado: **implementado (2026-11-05)**. `3` minimapa, `4` apagar/encender temporal; `T` tiempo dev.
- Archivos: `dev_input.py`, `game.py`, `ui.py`, locales.

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
- Estado: **decidido (D8)**: Energía, Extracción, Soporte Vital, Red Logística, Investigación y Defensa. La trampa va en Extracción.
- Nota: con scroll en el modal, el espacio deja de ser criterio; la categoría se elige por semántica.

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
- Propuesta: carrusel horizontal de 5 etiquetas; la seleccionada al centro; vecinas con alpha decreciente; izquierda/derecha cambia y mantiene el centro; wrap-around. **Animación slide/fade desde ya** (D11).
- Impacto: `ui.py`/`ui_modals.py`, `BuildController.menu_category` (ya hace wrap), locales y tests.

### 2. Módulos y red

**B11 — Estación de monitoreo**
- Feedback: “crear un módulo ‘estación de monitoreo’ o similar para ver cuánto consume y produce toda la red”.
- Estado: **decidido (D7)**: híbrido. La Estación de monitoreo desbloquea la pantalla de red mientras esté online y conectada.
- Nota: definir coste, obra, energía y tecnología; la pantalla muestra consumo/producción por recurso, balance neto, módulos activos/offline, caps y cuellos de botella.
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
- Estado: **decidido (D9)**: 6 comida/d y 3 O₂/d; coste propuesto 10 Cmp; resto sin cambios (1,5 d, 3 E/d, 4 agua/d).
- Actual: 8 Cmp, 1,5 d, 3 E/d, 4 agua/d → 10 comida/d + 2 O₂/d.
- Pendiente: confirmar coste final y el sink de comida (biodiésel/combustible y trampas).

**B16 — Extractores sin agua**
- Feedback: “revisar los extractores de agua sin agua; deberían consumir por estar encendidos”.
- Estado: **implementado (2026-11-05)**. No se auto-apagan; consumen **50% de su energía nominal** sin recursos y muestran **“sin recursos disponibles” en rojo**. Aplica a la mina y a futuros extractores.
- Implementación: extractor 2 E/d → 1 E/d; mina 3 E/d → 1,5 E/d; test actualizado.

**B17 — Trampa de peces**
- Feedback: ver “Decisiones generales”.
- Estado: **implementado (2026-11-05)**.
- Requisitos cumplidos: placement sobre agua, cable sobre agua, sin energía, 2 Cmp, 0,5 d, producción nocturna con tirada por hora (0 permitido, ~3/noche), parada al agotarse el agua, sin ruina y chatarra directa.
- Pendiente: tuning de distribución/ventana y fórmula exacta de chatarra.

### 4. Mundo y cámara

**B18 — Depósitos extra en el resto del mapa**
- Feedback: “no se están generando recursos en el mapa; revisar la generación de mundo”. Aclaración: no son los depósitos iniciales; el tester exploró todo el mapa y no encontró los depósitos extra/procedurales.
- Estado: **implementado con anillos difusos (2026-11-05)**. Antes, el generador creaba blobs procedurales con cobertura despareja (164 de 256 chunks de 64×64 sin depósitos); ahora hay cuota por región y más densidad hacia los bordes. Falta reproducir el save/build exacto del tester.
- Causa probable: 45+35 blobs aleatorios de radio 3-9 sobre 1M de tiles; no hay cuota mínima por región ni control de densidad por distancia. También puede influir un save viejo que conserva un mundo generado antes de un cambio.
- Otra hipótesis: el overlay de recursos solo se dibuja en tiles visibles, no en niebla explorada. Si el tester “exploró” con radar y miró la capa de recursos, las zonas en niebla se ven vacías aunque tengan depósitos.
- Acción: reproducir con save nuevo, seed y build; confirmar si miró en niebla o en zona visible; reemplazar la dispersión aleatoria por el esquema de anillos difusos (ver propuesta) y agregar tests de cobertura.

**B19 — Mundos aleatorios**
- Feedback: “ya podemos habilitar los mundos aleatorios”.
- Estado: **decidido en dirección (D5)**: la seed se guarda en el save y se usa para regenerar. Falta la UI de nueva partida/seed y el reroll.
- Nota técnica: hoy `WORLD_SEED` es fijo y `load_game()` llama `generate_world()` sin seed. Hay que leer `size`/`seed` del save y regenerar con ellos; implica cambio de formato/versión.
- Decidir: seed visible, reroll, mundos compartidos por seed y compatibilidad con saves v4.

**B20 — Mapa más grande, chunks y generación dinámica**
- Feedback: “expandir a 2024” (probablemente 2048), “considerar sistema de chunks y generación dinámica”.
- Estado: **decidido**: tamaño parametrizable con default 2048 en la próxima etapa. Chunks/dinámico queda para después, pero el generador se diseña con coordenadas de chunk.
- Contexto: hoy `WORLD_SIZE=1024` y el mundo son listas planas de ~1M de tiles; 2048 serían ~4M. Chunks/dinámico cambia generación, visión, save, cámara, radar y depósitos.
- Acción: implementar `World(size)`, save con `size`/`seed`, arrays compactos y benchmark de memoria en R36S.

**B21 — Bosques y cristales**
- Feedback: “metamos de una vez bosques y cristales”.
- Estado: **decidido (D10)**: se agregan ya bosques, carbón y cristales, aunque no se puedan usar. Bosque cercano garantizado, carbón en el borde explorado y cristales en grupos de 2-3/4-5 puntos.
- Pendiente: interacción de árboles/brotes, visibilidad de yacimientos subterráneos y usos futuros.

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

- **Etapa 1 (ahora):** mapa parametrizable con default **2048**, arrays compactos para memoria, muestreo por chunks con perfil radial y contenido nuevo (bosques/carbón/cristales).
- **Etapa 2 (mundos aleatorios):** guardar la seed en el save y regenerar con ella; sumar UI de nueva partida/seed y reroll.
- **Etapa 3 (chunks/dinámico):** generar chunks bajo demanda con el mismo campo; guardar chunks modificados y no todo el mapa. Necesario para mapas aún más grandes o infinitos.

**Decidido:** más recursos hacia afuera; los raros (cristales) escasos cerca y más hacia los bordes; cristales en grupos de 2-3 puntos (4-5 los grandes); bosque cercano garantizado y carbón en el borde explorado.
**A afinar:** cantidad y ancho de anillos, tamaño de chunk, cuota mínima por región, curvas por recurso, visibilidad de los anillos y de los yacimientos subterráneos.

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

## Triage

> Estado al 2026-11-05.

| Bucket | Items |
|--------|-------|
| **Hecho (etapas 0-3)** | B04, B05, B07, B09, B12, B13, B30, B18, B19, B20, B21, B31, B32, B10, B17, B16, B15, B14 (biodiésel), créditos |
| **Etapa 4** | B01 (rename cable), B02 (cables libres/recálculo), B06 (menú A+A), B08 (cámara), B11 (monitoreo), D7 |
| **Etapa 5 / backlog** | extracción/uso de carbón/cristal, combustible/combate, B22-B29 |

## Decisiones explicadas (ronda 2)

> Cada punto conserva el contexto y la decisión tomada. Lo que queda “pendiente” son detalles de implementación o tuning, no la dirección.

### Estado de las decisiones (ronda 2)

| ID | Decisión tomada | Pendiente |
|----|-----------------|-----------|
| D1 | Nocturna, una tirada por hora, 0 permitido, ~3/noche | Afinar distribución y ventana exacta |
| D2 | Sin auto-apagado; 50% de energía sin recursos; aviso rojo “sin recursos disponibles” | Confirmar textos/estado para mina y futuros extractores |
| D3 | Colocación libre de cables, con estado conectado/desconectado | Definir overlay y reglas de visión |
| D4 | 3=minimapa, 4=apagar/encender temporal; WASD cursor, flechas cámara | Reasignar 4 en la etapa 4 (A+A) |
| D5 | Tamaño parametrizable; default 2048 ahora | Benchmark de memoria en R36S |
| D6 | Anillos difusos + rareza por distancia + bosques/carbón/cristales ahora | Algoritmos, curvas y visibilidad subterránea |
| D7 | Híbrido: módulo desbloquea pantalla de red | Coste/energía/tecnología |
| D8 | Energía, Extracción, Soporte Vital, Red Logística, Investigación, Defensa; trampa en Extracción | Aplicar nombres en código/locales |
| D9 | Invernadero 6 comida/d + 3 O₂/d | Coste final y sink de comida |
| D10 | Todo el contenido de mundo ahora, aunque no se pueda usar | Interacción de árboles/brotes |
| D11 | Animaciones de menú ahora | Alcance exacto (scroll/carrusel/modales) |

### D1 — Trampa: ventana de producción y RNG

**Decisión:** producción exclusivamente nocturna, con **una tirada por hora de noche**, incluyendo 0, para un promedio de **3 comida por noche**.
**Contexto:** el plan original decía 1-2 comida/noche; la decisión nueva sube el promedio a 3. El tick es continuo, así que la tirada no puede ser por tick: se evalúa al cruzar cada hora de la ventana nocturna.
**Implementación propuesta:**
- Ventana: **20:00–04:00** (8 horas de noche plena según `daylight.natural_light`). Si se incluye crepúsculo, la ventana y la media por hora cambian.
- Media por hora: `3 / 8 = 0,375`.
- Distribución simple que permite 0, 0.X y X.Y: **50% de 0**; si no, `uniform(0, 1,5)` (media 0,75). Media por hora: 0,375; por noche: 3.
- Cada tirada se pierde si la trampa está apagada, desconectada o sin agua.
- El panel muestra “Noche” mientras produce y “En espera” de día.
**Afinar en playtest:** probabilidad de 0 y techo de la uniforme; la media por noche debe quedar en 3.
**Impacto:** `module_tick`, `module_defs.effective_flow`, panel y tests.

### D2 — Extractor sin agua

**Decisión:** el extractor **no se auto-apaga**. Si no hay recursos, sigue encendido y consume **50% de su energía nominal**; se apaga manualmente desde el menú del módulo. El panel muestra **“sin recursos disponibles” en rojo**, sin más detalles. Aplica a la mina y a futuros extractores.
**Contexto:** hoy `_job_extractor` devuelve `None` sin depósito y el test `test_depleted_extractor_does_not_consume_power` afirma consumo cero. Hay que cambiar el comportamiento y el test.
**Implementación:**
- Extractor de agua: nominal 2 E/d → **1 E/d** sin agua.
- Mina: nominal 3 E/d → **1,5 E/d** sin mineral.
- El 50% entra como demanda normal de energía; si la red no alcanza, se aplica el reparto proporcional existente.
- El estado rojo no explica el motivo (no “depósito agotado”): solo “sin recursos disponibles”.
**Impacto:** `module_tick`, tests, panel y balance energético.

### D3 — Cables en cualquier punto

**Decisión:** **colocación libre** de cables. Se puede construir en cualquier tile válido (suelo o agua), aunque el tramo quede desconectado; al tocar la red se conecta.
**Contexto:** hoy `_cable_preview` exige adyacencia a la red conectada o al tramo actual; no se pueden dejar tramos desconectados. El tester pidió libertad y revisar el recálculo al destruir.
**Implementación:**
- Cables desconectados: se dibujan distintos y no dan visión ni alimentan módulos.
- Al conectar un tramo, se invalida el caché y se recalcula la red.
- Al demoler, se invalida el caché y los módulos que quedan sin camino pasan a offline.
- Tests: tramo desconectado no alimenta; al conectarse, sí; al cortar, vuelve a offline.
**Reglas:** cable sobre agua permitido; sobre roca no.
**Impacto:** `construction`, `network`, `demolition`, `vision`, `ui_map` y save.

### D4 — Remapeo PC

**Decisión:** remapeo PC cerrado.
**Mapa final:**
- `1`/`2`: zoom in/out.
- `3`: minimapa.
- `4`: libre (reservado para overlay de red/estación de monitoreo).
- `Tab`: menú de construcción.
- `E`: aceptar.
- `Q`: recursos.
- `Esc`: B / volver.
- `J`: duplicado de A; `K`: duplicado de B.
- **DPAD de teclado:** se elimina; WASD=mueve cursor y flechas=mueven cámara. J/K dejan de ser DPAD_LEFT/DOWN.
- Enter/START y Backspace/SELECT se mantienen.
**Contexto:** hoy J/K son DPAD_LEFT/DOWN, E/Q son R1/L1 y 3/4 serían R1/R2. El menú A+A elimina R1 (apagar), así que 3 pasa a minimapa y 4 queda libre.
**Impacto:** `dev_input`, `DEV_KEYMAP`, ayuda y tests.

### D5 — Tamaño de mapa: 2024/2048

**Decisión:** **tamaño de mundo parametrizable** y **default 2048** en la misma etapa que la generación nueva. Chunks/dinámico queda para después, pero el generador debe diseñarse con coordenadas de chunk.
**Contexto:** hoy 1024² = ~1M tiles en listas planas; 2048² = ~4M. Con listas de Python el costo de memoria puede ser alto para R36S. Chunks/dinámico es un refactor grande de `World`, save, visión, radar y cámara.
**Implementación:**
- `World(size=...)` y `generate_world(seed, size)`; `HABITAT_X/Y` calculados en runtime.
- `--world-size` o config; default **2048**. El save guarda `size` y `seed`.
- `load_game` lee `size` del save y genera con ese tamaño; no fuerza 2048 a saves viejos de 1024.
- Cámara, visión, radar y `clamp_cursor` usan `world.size`, no la constante `WORLD_SIZE`.
- Para que 2048 sea viable: `tiles`/`deposits` como `bytearray` o `array('B')`, `deposit_amounts` como `array('f')`; `explored`/`visible` ya son bytearrays.
- Benchmark obligatorio: tiempo de generación, memoria y FPS en PC y R36S.
**Pendiente:** medir memoria real; decidir si 2048 es el default de nuevas partidas o solo una opción.
**Impacto:** `config.WORLD_SIZE`, `world`, `camera`, `savegame`, `vision`, tests.

### D6 — Generación de depósitos y anillos difusos

**Decisión:** **anillos difusos + rareza por distancia**. Cuanto más lejos del centro, más recursos en general; los raros (cristales) son escasos cerca y aumentan hacia los bordes. Se agregan ya bosques, carbón subterráneo y cristales, aunque todavía no se puedan extraer.
**Contexto:** el generador actual crea blobs aleatorios; 64% de chunks de 64×64 quedan vacíos. El tester exploró y lo percibió vacío. La propuesta de anillos difusos está arriba.
**Contenido nuevo decidido:**
- **Bosque cercano garantizado:** pequeño, bloquea construcción, se puede destruir manualmente y da **madera** directamente; deja **brotes**. Los brotes se pueden destruir y no dan nada. Regrow posterior.
- **Carbón:** yacimientos subterráneos; se garantiza uno en el borde de lo explorado, aunque no se pueda usar todavía.
- **Cristales:** yacimientos subterráneos finitos; aparecen como **puntos dispersos**: grupos de 2-3, y los más grandes de 4-5. No son un parche continuo.
- **Recursos nuevos:** madera, carbón, combustible (biodiésel) y cristales. Madera tiene fuente (árboles); carbón/cristal/combustible quedan sin uso hasta sus extractores/producción.
**Algoritmos a evaluar/afinar:**
- Envolvente radial `ρ(d)` con `smoothstep` + ruido coherente (simplex/value) para romper simetría.
- Muestreo por chunk con Poisson-disk (Bridson), jittered grid o best-candidate; cuota mínima por chunk/anillo.
- Vetas subterráneas de carbón con random walks o ruido celular.
- Cristales con muestreo de puntos alrededor de un centro de grupo (2-3 o 4-5), sin rellenar discos.
- Rechazo por colisión con agua, roca, ruinas, hábitat y otros depósitos.
**Pendiente:** curvas exactas por recurso, tamaño de chunk, mínimo por región, si los yacimientos subterráneos se ven desde el inicio o solo con radar/tecnología, y si el carbón garantizado queda en el borde del área inicial o del frente explorado.
**Impacto:** `world`, `config`, `savegame` (seed/size), tests, debug overlay, assets y catálogo.

### D7 — Estación de monitoreo

**Decisión:** **híbrido**. Se construye una **Estación de monitoreo**; mientras esté online y conectada, desbloquea una pantalla de red con consumo/producción por recurso, balance neto, módulos activos/offline, caps y cuellos de botella.
**Contexto:** el modo recursos ya muestra cantidades, caps y tendencia global; no hay desglose por módulo ni balance de red en un solo lugar.
**Pendiente:** coste, obra, energía, tecnología y si la pantalla requiere el módulo online o alcanza con tenerlo construido.
**Impacto:** `module_defs`, `module_kind`, `config`, UI, save y tests.

### D8 — Nombres de categorías y ubicación de la trampa

**Decisión:** categorías finales:
- **Energía**
- **Extracción**
- **Soporte Vital**
- **Red Logística**
- **Investigación**
- **Defensa**
**Trampa de peces:** **Extracción** (saca comida del agua). El scroll del menú elimina la restricción de espacio.
**Impacto:** `BUILD_CATEGORIES`, locales, docs y tests. Mantener los IDs internos; solo cambian los nombres visibles.

### D9 — Invernadero, trampa y sink de comida

**Decisión:** invernadero **6 comida/d** y **3 O₂/d**. Se mantiene la dirección de “más caro” y el resto de los consumos.
**Números propuestos:** 10 Cmp (a confirmar), 1,5 d, 3 E/d, 4 agua/d, 6 comida/d, 3 O₂/d.
**Sink de comida:** biodiésel/combustible y fabricación de trampas; el resto de usos (fabricador Mk II, bichos/eventos) queda para después.
**Contexto:** hábitat −8/d; invernadero +10/d; trampa +3/d promedio. Sin sink, la comida se acumula.
**Pendiente:** confirmar coste final y si el invernadero sigue siendo la fuente principal o pasa a complementaria.
**Impacto:** `config`, `module_defs`, catálogo, tests y balance.

### D10 — Bosques y cristales

**Decisión:** **meter todo de una**, aunque todavía no se pueda usar. Estamos en beta testing y se asume el contenido incompleto.
**Contexto:** el plan anterior los dejaba para el slice 7 hasta tener un uso concreto. La generación por anillos debe incluirlos.
**Alcance decidido:**
- Bosques, carbón subterráneo y cristales en la generación.
- Recursos madera, carbón, combustible y cristales en el pool/UI.
- Bosque cercano garantizado y carbón garantizado en el borde explorado.
- Extracción/uso de carbón, cristal y combustible queda para etapas posteriores.
**Pendiente:** interacción exacta de árboles/brotes (qué tecla, si el brote bloquea construcción, cuánto tarda el regrow), visibilidad de yacimientos subterráneos y cantidad de madera por árbol.
**Impacto:** `world`, `config`, `module_defs`, `tech_defs`, assets, save y anillos.

### D11 — Detalles del modal y del selector

**Decisión:** **animaciones de menú desde ya**, para dejar la infraestructura lista.
**Implementación propuesta:**
- Scroll vertical animado de tarjetas (suavizado hacia la selección).
- Carrusel de categorías con slide y fade; la selección queda centrada y las vecinas se difuminan hacia los bordes.
- Evaluar en el mismo pase una transición suave de apertura/cierre de modales si no complica el input.
- 4 tarjetas visibles y 5 etiquetas de categoría como punto de partida; ajustar según el contenido.
**Pendiente:** si el scroll/carrusel hace wrap en los extremos y cuánto dura la animación.
**Impacto:** `ui.py`, `ui_modals.py`, `BuildController` y tests.

## Etapas

> Secuencia actualizada al 2026-11-05.

| Etapa | Estado |
|-------|--------|
| **0. Quick fixes beta** | **Hecho** — remapeo PC, créditos/layout, icono de agua, cables grises, copy del laboratorio, tiempo dev |
| **1. Mundo 2048 + generación** | **Hecho** — tamaño parametrizable, arrays compactos, save size/seed, anillos difusos, bosques/carbón/cristales y recursos nuevos |
| **2. UI de construcción** | **Hecho** — scroll, carrusel animado, nombres y animaciones |
| **3. Trampa + comida + extractores** | **Hecho** — RNG nocturna, extractor/mina al 50%, invernadero 6/3, biodiésel como sink |
| **4. Red y módulos** | **Siguiente** — rename de cable, cables libres, menú A+A, cámara y estación de monitoreo |
| **5. Contenido/late game** | **Backlog** — extracción/uso de carbón/cristal, combustible/combate, eventos y Mk II |

**Notas:**
- Benchmark 2048 en PC: ~60 ms de generación, ~40 MB de arrays y ~3,9 ms por frame de mapa; falta medir en R36S.
- La etapa 4 depende del menú A+A y del rename de cable.
- La etapa 5 no debería abrirse antes de estabilizar la 4.

## Archivos probablemente afectados

| Área | Archivos |
|------|----------|
| Input/controles | `dev_input.py`, `game_input.py`, `game.py`, `ui_input.py`, `game_help.py`, `locales/es.json` |
| Red/cables | `construction.py`, `network.py`, `demolition.py`, `ui_map.py`, `ui_theme.py` |
| Módulos/UI | `module_kind.py`, `module_defs.py`, `config.py`, `ui.py`, `ui_panel.py`, `locales/es.json` |
| Mundo/cámara | `world.py`, `config.py`, `camera.py`, `savegame.py`, `vision.py` |
| Créditos | `credits.py`, `locales/es.json` |
| Assets | `assets/icons/water.png`, `assets/icons/cable.png`, `docs/assets.md` |
| Tests | `test_sim.py` (input, red, extractor, trampa, save, generación) |

## Referencias

- [plan.md](plan.md) — roadmap y decisiones cerradas.
- [catalogo.md](catalogo.md) — módulos, categorías y números.
- [diseno-juego.md](diseno-juego.md) — loop, sistemas y controles.
- [assets.md](assets.md) — sprites, prompts y seeds.
- [estado.md](estado.md) — estado actual y próximos pasos.
