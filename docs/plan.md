# Plan

> Fuente única del roadmap. Catálogo de módulos/tecnologías: [catalogo.md](catalogo.md). Estado: [estado.md](estado.md). Código: [arquitectura.md](arquitectura.md). Juego: [diseno-juego.md](diseno-juego.md).
>
> Regla: un slice a la vez. 4B/4C, UI/balance, playtest, fundación de recursos/costes y chatarra/reciclador/demolición están cerrados. **Beta etapas 0-4 (2026-11-05)** implementadas: remapeo/créditos/iconos, mundo 2048 con anillos, UI de construcción, trampa/comida y red/módulos. **Fase 5 (2026-11-06)** implementada: generador eléctrico multi-combustible, tecnologías de solar/carbón/cristal/almacenamiento y batería. Ahora toca **v6**: usos de cristales, tanques especializados, combate/eventos y prerequisitos tecnológicos.
>
> Feedback beta de TxxT (2026-11-05): [beta-txxt.md](beta-txxt.md). Las decisiones de las etapas 0-4 y de la fase 5 están implementadas; v6 queda como siguiente bloque.

## Norte

Gestión y supervivencia en un mapa 2D: red de módulos, recursos, luz y mantenimiento desde la consola del astronauta. La base es jugable, el playtest cerró y el loop de chatarra/reciclador ya está implementado. El próximo foco es la **UX de red y módulos** (etapa 4); después, energía y contenido.

## Estado actual (hecho)

- Mapa parametrizable con default 2048×2048 (`--world-size`/`SOLITUDINE_WORLD_SIZE`), arrays compactos, cámara, niebla, cables, módulos, buffers, depósitos finitos y muerte por O₂/agua/comida.
- UI 640×480 en grilla de 16 px, sprites, zoom, minimapa, día/noche y lámpara.
- **4B:** laboratorio, investigación de un nodo a la vez, pantalla de Tecnología y desbloqueos.
- **4C:** electrolizador y condensador; O₂ y agua tienen dos fuentes.
- **UI/balance (2026-10-29):**
  - Barra superior con O₂, agua, comida y energía, nombre y `x/y`; mineral/componentes fuera de la barra.
  - Modo recursos (X/C) con los once recursos, nombre, cap, tendencia y días de los vitales.
  - Menú de construcción con pestañas por categoría, navegación izquierda/derecha, categorías vacías filtradas, bloqueados/no pagables en gris y faltantes por recurso.
  - Panel de módulo con estado real, descripción, producción/consumo con nombre de recurso y día de construcción; buffer, reserva y progreso.
  - Badges de modo/pausa (`RECURSOS`, `CONSTRUIR`, `COLOCAR`, `PAUSA`), celda seleccionada marcada y X disponible en modo colocar.
  - Menú de pausa con Continuar/Créditos; créditos con scroll y easter egg.
  - **Correcciones de playtest (2026-10-29):** hábitat solo con consumo y alertas; recursos sin gasto diario y A vuelve a inspección; construcción con iconos, sin cap de componentes, modal de altura fija con controles al pie y categoría `< >`; estados sin paréntesis.
  - **Tecnología y muerte (2026-10-29):** A otra vez sobre el laboratorio inspeccionado abre Tecnología; SELECT queda libre. La muerte guarda el estado de game over y al reabrir se mantiene.
  - **Arranque (2026-10-29):** splash de texto best-effort en el lanzador antes del runtime; splash con pygame que se mantiene durante assets/guardado/mundo; joystick e inicialización pesada diferidos; al terminar pide START.
  - **Playtest UI (2026-10-29):** red logística única para cualquier módulo; almacén no apagable; menú de construcción con descripción y flujos produce/consume; bloqueos dicen “Investigar”; modales de menú más grandes; TxxT en créditos.
- **Playtest (2026-10-29):** cerrado; los ajustes aplicados quedaron absorbidos por la pasada de UI/balance.
- Guardado `VERSION` 4; sin migración (los saves viejos se borran). 82 tests de regresión.

## Hecho: fundación de recursos/costes + chatarra (2026-10-29)

**Fundación**

- Pool único (originalmente siete recursos: O₂, agua, comida, energía, mineral, componentes y chatarra; hoy once con madera, carbón, combustible y cristales); `ResourceId`/`ResourceDef` y caps por recurso.
- `Cost` multi-material con pago atómico, `missing`, reembolso y `Module.cost_paid`.
- Fabricador: **5 Cmp + 2 mineral**; la mina sigue solo con componentes para no bloquear el arranque.
- Save `VERSION` 4 **sin migración**: al cargar un save viejo se borra y se empieza de cero.
- UI: coste con iconos/cantidades, faltantes por recurso; barra superior y modo recursos desde el registro.

**Chatarra, ruinas y reciclador**

- 26 ruinas (2 garantizadas cerca del hábitat, 24 procedurales), 1 tile y 4-10 chatarra; bloquean construcción y cable.
- Recogida con **A** sobre la ruina seleccionada (A para seleccionar, A otra vez para recoger); cap de chatarra 30 (+40 por almacén); el remanente queda guardado.
- **Demolición:** con un módulo o cable seleccionado, **B** abre confirmación y **A** demuele. Un módulo deja una ruina con 0,6-0,9 del equivalente mineral; el cable devuelve 1 Cmp.
- **Cancelar obra:** componentes pagados × `min(progreso, 0,9)` en chatarra; el resto de materiales se pierde.
- **Reciclador:** 3 Cmp, 0,5 d, 1 E/d, 0,5 agua/d; 4 chatarra/d → 3,6 mineral/d + 0,2 Cmp/d; registra chatarra procesada y mineral reciclado.
- **Tecnología `reciclaje`:** T1 provisional (el árbol T2 se armará después), 5 chatarra + 2 Cmp + 1 mineral, 2 d; requiere laboratorio.
- 66 tests de regresión; `make test` verde.

## Hecho: beta etapas 0-3 (2026-11-05)

- **Etapa 0:** remapeo PC (1/2 zoom, Tab construir, E aceptar, Q recursos, Esc B, J/K A/B; 3 minimapa, 4 apagar/encender), tiempo dev con `T`, copy del laboratorio, créditos y layout, icono de agua y cables grises.
- **Etapa 1:** mundo parametrizable default 2048, arrays compactos (40 MB), save con `size`/`seed`, generación por anillos difusos, bosques/carbón/cristales y recursos de madera/carbón/combustible/cristales.
- **Etapa 2:** scroll vertical y carrusel animado de categorías; nombres Energía/Extracción/Soporte Vital/Red Logística/Investigación/Defensa.
- **Etapa 3:** trampa de peces (RNG nocturna, sin ruina), extractor/mina al 50% sin recursos, invernadero 6 comida/3 O₂ y procesador de biodiésel como sink de comida.
- Criterio cumplido: placement sobre agua, cable sobre agua, producción nocturna con RNG, parada al agotarse el agua y guardado.

## Hecho: etapa 4 — red y módulos (2026-11-05)

- Cables de **colocación libre**, también desconectados; la red se recalcula al construir/demoler.
- **Menú contextual A+A** en todos los módulos: investigación, red, encender/apagar, demoler y cerrar. Se retiró el apagado con R1 y la demolición de módulos con B; B queda para cables.
- **Cámara hasta los bordes** del mapa; el cursor sigue limitado a lo explorado.
- **Estación de monitoreo** (6 Cmp, 1,5 d, 2 E/d) con pantalla de red en dos columnas (producción/consumo) por recurso, energía y módulos online/offline/en obra.
- Rename visible de **Cable → Enlace**; el ID `cable` no cambia.
- **Modales unificados:** `ui_modals.draw_modal` centraliza título, subtítulo, columnas, scroll y ayuda; todos son anchos. La red usa dos columnas (producción/consumo) con icono + nombre.
- **Beta PC:** solo 2x; se eliminó la variante intermedia.

## Hecho: fase 5 — energía, cristales y almacenamiento (2026-11-06)

- **Generador eléctrico** desde el inicio, apagado y sin combustible; consumo fijo de 1 unidad/día y salida 5/12/20 E/d según madera/carbón/biodiésel.
- **Menú A+A declarativo:** acciones por módulo en `ModuleDef.menu_actions`, registro central y submenú de combustible; laboratorio, monitor, almacén, generador y hábitat comparten el mismo motor.
- **Tecnologías:** Fotovoltaica (3 Cmp), Minería de carbón (4 Cmp), Cristalografía (10 Cmp + 8 biodiésel), Almacenamiento especializado (6 Cmp + 2 mineral).
- **Cristalografía:** desbloquea el extractor de cristales; no usa cristal en el coste. Los cristales quedan sin uso hasta v6.
- **Batería:** +100 cap de energía, detrás de Almacenamiento especializado.
- **Almacén general:** +40 a recursos generales; no energía ni O₂.
- **v6:** usos de cristales, tanque de O₂, tanques especializados de agua, combate/eventos, prerequisitos y tecnologías que solo desbloquean otras tecnologías.

## Decisiones cerradas

### Recursos

- La regla de **2 fuentes / 2 usos** es una heurística, no una regla estricta. Se acepta una excepción si resuelve un problema claro y no deja un recurso de un solo uso.
- Recursos actuales: O₂, agua, comida, energía, mineral, componentes, **chatarra**, **madera**, **carbón**, **biodiésel** y **cristales**.
- Recursos incorporados (2026-11-05): **madera**, **carbón**, **biodiésel** (producido) y **cristales**. Madera sale de árboles; el biodiésel se produce en el procesador; el carbón y los cristales tienen extractores con tecnología.
- La matriz completa vive en este plan; el catálogo define módulos/tecnologías.

### Chatarra, ruinas y reciclador

- La chatarra entra a la red, tiene cap propio de **30** (+40 por almacén) y se muestra en modo recursos.
- Se recoge de ruinas desde el día 0 con **A** sobre la ruina seleccionada; el monto es variable (4-10) y el remanente queda guardado.
- Ruinas: **26** (2 garantizadas cerca del hábitat, 24 procedurales), 1 tile; solo en zonas abiertas sin agua/mineral/árboles/cristales; bloquean construcción y cables; se guardan.
- Demoler un módulo crea una ruina de su tamaño (hoy 1×1). La recogida es instantánea y sin coste.
- Demolición con **B** sobre el módulo/cable seleccionado y confirmación con **A**; el módulo deja una ruina con 0,6-0,9 del equivalente mineral. El cable devuelve 1 Cmp íntegro.
- Cancelar una obra devuelve chatarra equivalente a los componentes pagados × `min(progreso, 0,9)`; los materiales extra no componentes se pierden.
- Reciclador: 3 Cmp, 0,5 día, 1 E/d y 0,5 agua/d; 4 chatarra/d → 3,6 mineral/d + 0,2 Cmp/d; registra chatarra procesada y mineral reciclado.
- Investigación `reciclaje`: T1 provisional (el árbol T2 se armará después), 5 chatarra + 2 Cmp + 1 mineral, 2 días; requiere laboratorio.
- No vuelve obsoleta a la mina: la chatarra es limitada, RNG y menos abundante; cierra el ciclo de lo construido y da una segunda fuente de mineral.

### Comida, trampas y biodiésel

- La comida es un problema recurrente. Se gastará en fabricar biodiésel/combustible y en la fabricación de trampas.
- **Invernadero** (implementado 2026-11-05): 10 Cmp, 1,5 d, 3 E/d, 4 agua/d → **6 comida/d + 3 O₂/d**.
- **Trampa de peces** (inicial): 2 Cmp, 0,5 d; se coloca sobre agua y se conecta a la red aunque no consuma energía; produce solo de noche, con una tirada por hora (0 permitido) y ~3 comida/noche en promedio; no es fuente primaria salvo en cantidad; si el agua se agota, queda inútil para siempre y se puede demoler para recuperar chatarra. No deja ruina: la demolición da chatarra directa.
- El cable puede ir sobre agua. La trampa es un módulo aparte y no comparte tile con el extractor.
- La **trampa de defensa** queda para cuando exista combate.
- **Biodiésel:** recurso producido, no extraído; su módulo/productor y consumidor se definirán más adelante. Cuando dos módulos o la supervivencia compiten por un recurso, el jugador controla apagando módulos; el reparto es igualitario y los empates se resuelven al azar.

### Agua y exploración

- **Generación por anillos difusos** (feedback beta 2026-11-05): la densidad de recursos crece con la distancia al hábitat; los raros (cristales) son escasos cerca y aumentan hacia los bordes; cuota mínima por región para evitar zonas vacías. Ver [beta-txxt.md](beta-txxt.md).
- **Mapa parametrizable** con default **2048×2048**; el save guarda `size` y `seed`; arrays compactos para que entre en R36S. Chunks/dinámico queda para después.
- El agua tiene un depósito garantizado; los depósitos extra usan generación por anillos difusos. Es finita y no se regenera.
- El radar es la única exploración permanente y encuentra todo (incluidos ruinas, bosques y cristales).
- Quedarse sin energía puede matar por sed a través del condensador; se acepta.
- Cuando un depósito se agota, el tile vuelve a suelo; extractor y trampa quedan inútiles.

### Energía y generador

- Extractores y minas sin recursos **no se auto-apagan**: consumen **50% de su energía nominal** mientras estén encendidos y el panel muestra **“sin recursos disponibles” en rojo**. Se apagan manualmente; aplica a futuros extractores.
- **Generador eléctrico:** disponible desde el inicio, sin tecnología. Se crea **apagado y sin combustible elegido**. Consume **1 unidad/día** y produce según el combustible: madera **5 E/d**, carbón **12 E/d**, biodiésel **20 E/d**. El menú A+A permite elegir combustible; si no hay selección o se agota, pasa a apagado.
- **Panel solar:** requiere la tecnología barata **Fotovoltaica**. Sigue produciendo 12 E/d repartidos durante el día; no es variable, así que no lleva `~`.
- **Notación `~`:** se usa para promedios/rangos (trampa `~3/noche`, generador `5~20 E/d`), no para valores exactos.
- **Almacén general:** +40 a los recursos generales, pero **no energía ni O₂**. Esos caps quedan para almacenamientos especializados.
- **Batería:** módulo especializado detrás de **Almacenamiento especializado**; suma **+100 de cap de energía**. No reemplaza al almacén general.
- El tanque de O₂ y los tanques de agua especializados quedan para v6, con investigación propia.

### Bosques y cristales

- Son contenido base, no DLC; su implementación debe servir para probar la creación parametrizable de recursos para un DLC.
- **Implementados 2026-11-05:** bosques, carbón subterráneo y cristales. El carbón se desbloquea con **Minería de carbón** y los cristales con **Cristalografía**.
- **Bosque cercano garantizado:** pequeño, bloquea construcción; **A** tala y da 6-10 de **madera** directamente; deja **brotes**. **A** sobre un brote lo quita sin dar nada. Regrow queda pendiente.
- **Carbón:** yacimientos subterráneos; se garantiza uno en el borde del área explorada inicial. Alimenta el generador eléctrico; el extractor requiere una investigación inicial barata.
- **Cristales:** yacimientos subterráneos finitos; se generan como **puntos dispersos**: grupos de 2-3, y los más grandes de 4-5; no son un parche continuo. Se garantiza al menos un grupo hacia los bordes. El extractor queda detrás de **Cristalografía**, una investigación cara pagada con biodiésel; no se usa cristal en su coste para evitar un ciclo. Los cristales no tienen uso todavía.
- Recursos nuevos: **madera, carbón, biodiésel y cristales**. Madera y carbón alimentan el generador; el biodiésel se produce en el procesador; los cristales quedan reservados para v6.
- Pendiente: regrow de brotes, visibilidad de yacimientos subterráneos y curvas de rareza por distancia.

### Red y módulos

- **Cables de colocación libre:** cualquier tile válido (suelo o agua), incluso desconectado; al tocar la red se conecta y al cortar se recalcula.
- **Menú contextual A+A:** A selecciona, A abre el menú; desde ahí se investiga, se ve la red, se enciende/apaga, se demuele o se cierra. Se retiraron R1 (toggle) y B (demolición de módulos); B queda para cables.
- **Cámara dinámica:** puede llegar a los cuatro bordes del mapa; el cursor sigue limitado a lo explorado.
- **Estación de monitoreo:** 6 Cmp, 1,5 d, 2 E/d; si está online y conectada desbloquea la pantalla de red con producción y consumo en dos columnas, energía y módulos online/offline/en obra.
- **Rename visible:** Cable → **Enlace**; el ID interno `cable` no cambia para no romper saves.
- **Fase 5:** generador eléctrico desde el inicio, menú de combustible, tecnologías de solar/carbón/cristal/almacenamiento y batería. El menú A+A es declarativo y reutilizable: cada módulo aporta acciones y la UI solo las renderiza.

### UI

- Barra superior solo con los cuatro vitales, con nombres; si no caben, se decide en playtest.
- Modo recursos: once recursos (incluye madera, carbón, combustible y cristales); sin gasto diario ni días. A inspecciona y vuelve al terreno.
- Panel del hábitat: solo consumo diario por vital y alertas; las cantidades/caps viven en modo recursos.
- Menú de construcción por pestañas; categorías vacías ocultas; no disponibles en gris con “Investigar”; coste, faltante, descripción y flujo produce/consume visibles. Cada módulo se muestra como tarjeta horizontal con icono, borde/fondo propio y la seleccionada resaltada en ámbar. Coste multi-material con un icono+cantidad por recurso y faltantes por recurso; **modal con scroll vertical animado para N tarjetas** y controles en pie separado; **selector de categorías circular con slide/fade**, selección centrada y etiquetas difuminadas hacia los bordes (feedback beta 2026-11-05).
- Panel de módulo: estado, descripción, producción/consumo con nombres y día de construcción. Los módulos mixtos muestran ambas cosas; el reciclador muestra chatarra procesada y mineral reciclado.
- Ruinas: se dibujan en el mapa, se inspeccionan en el panel y se recogen con A. La demolición/cancelación abre un modal con confirmación A/B.
- Acciones especiales: cada módulo declara sus acciones de menú; con el módulo activo e inspeccionado, A abre el menú y la acción elegida se despacha desde un registro central. SELECT queda libre. El cable forma una red logística única que conecta módulos de cualquier tipo; el almacén y la batería no se pueden apagar.
- **Menú contextual A+A (feedback beta 2026-11-05):** todos los módulos abren un menú con A+A (seleccionar y abrir). Apagar y demoler salen del menú, sin teclas dedicadas; el laboratorio conserva A+A para investigar. Pendiente de diseño de UI.
- **Categorías (feedback beta 2026-11-05):** Energía, Extracción, Soporte Vital, Red Logística, Investigación y Defensa. La trampa de peces va en Extracción; el scroll del modal elimina la restricción de espacio.
- Badge de modo/pausa y celda seleccionada. X cambia capa también en modo colocar. Los estados son concisos, sin paréntesis explicativos.
- Sin menú de ayuda dedicado: la UI debe ser autoexplicativa; se mantienen los hints contextuales.
- Créditos en pausa con scroll y easter egg sin pistas. Reconocer a **TxxT** como beta tester, bugcatcher y aporte de ideas, y a **JuanDi (Juandi Alfa)** como alpha/beta tester y aporte de ideas (feedback beta 2026-11-05).

## Orden de implementación

1. ~~Playtest y correcciones.~~ Cerrado (2026-10-29).
2. ~~Fundación de recursos/costes.~~ Cerrado (2026-10-29).
3. ~~Chatarra/reciclador/demolición.~~ Cerrado (2026-10-29).
4. ~~Trampa de peces + comida.~~ Cerrado (2026-11-05).
5. ~~Mundo 2048 + generación.~~ Cerrado (2026-11-05).
6. ~~UI de construcción (scroll/carrusel/nombres).~~ Cerrado (2026-11-05).
7. ~~Red y módulos.~~ Cerrado (2026-11-05).
8. ~~Generador eléctrico multi-combustible + tecnologías solar/carbón.~~ Cerrado (2026-11-06).
9. ~~Cristalografía y extractor de cristales.~~ Cerrado (2026-11-06); cristales sin uso hasta v6.
10. ~~Batería y almacenamiento especializado.~~ Cerrado (2026-11-06); almacén general conserva +40 sin energía/O₂.
11. **v6:** usos de cristales, tanques de O₂/agua, combate/eventos, prerequisitos y tecnologías que solo desbloquean otras tecnologías.

> La retroalimentación beta 2026-11-05 se ejecutó en las etapas 0-4; ver [beta-txxt.md](beta-txxt.md).

## Matriz de recursos

| Recurso | Fuentes | Usos | Estado |
|---------|---------|------|--------|
| O₂ | Reserva inicial, invernadero (con agua), electrolizador | Soporte vital | Hecho |
| Agua | Extractor, condensador | Soporte vital, invernadero, electrólisis | Hecho |
| Energía | Panel solar; generador eléctrico (madera/carbón/biodiésel) | Casi todos los módulos | Hecho |
| Comida | Invernadero; trampa de peces | Soporte vital; biodiésel | Hecho |
| Mineral | Mina; reciclador | Fabricador | Hecho |
| Componentes | Fabricador | Construcción, investigación | Hecho |
| Chatarra | Ruinas, demolición | Reciclador, investigación | Hecho |
| Madera | Bosques (árboles) | Generador eléctrico (5 E/d) | Hecho |
| Carbón | Yacimientos subterráneos (extractor de carbón) | Generador eléctrico (12 E/d) | Hecho; extractor con tecnología barata |
| Cristales | Yacimientos subterráneos (extractor de cristales) | Reservados para v6 (láseres/tecnología avanzada) | Extracción con Cristalografía; uso pendiente |
| Biodiésel (`fuel`) | Procesador de biodiésel | Generador eléctrico (20 E/d) y Cristalografía | Hecho |

> 2 fuentes / 2 usos es deseable, no obligatorio. **Excepción de beta (2026-11-05):** se aceptan recursos sin fuente/uso completo (madera, carbón, combustible y cristales) para dejar la infraestructura y el contenido de mundo listos; se completan en etapas posteriores.

## Números actuales

| Parámetro | Valor |
|-----------|-------|
| Reservas iniciales | 12 O₂ / 9 agua / 7 comida / 10 energía (días) |
| Caps iniciales | 140 O₂ / 100 agua / 80 comida / 100 energía / 40 mineral / 80 Cmp / 30 chatarra / 60 madera / 60 carbón / 60 combustible / 40 cristales |
| Componentes iniciales / cap | 60 / 80 |
| Chatarra inicial / cap | 0 / 30 (+40 por almacén general) |
| Ruinas | 26 (2 garantizadas + 24 procedurales), 4-10 chatarra |
| Fabricador | 5 Cmp + 2 mineral, 2 d, 4 E/d, 6 mineral/d → 4 Cmp/d |
| Reciclador | 3 Cmp, 0,5 d, 1 E/d, 0,5 agua/d, 4 chatarra/d → 3,6 mineral/d + 0,2 Cmp/d |
| Investigación `reciclaje` | 5 chatarra + 2 Cmp + 1 mineral, 2 d (T1 provisional) |
| Laboratorio | 8 Cmp, 1,5 d, 3 E/d |
| Investigación T1 | 4 Cmp, 1,5 d |
| Electrolizador | 6 Cmp, 1 d, 4 E/d, 6 agua/d → 8 O₂/d |
| Condensador | 8 Cmp, 1,5 d, 6 E/d → 8 agua/d |
| Radar | 8 Cmp, 1,5 d, 12 E/d |
| Invernadero | 10 Cmp, 1,5 d, 3 E/d, 4 agua/d → 6 comida/d + 3 O₂/d (O₂ requiere agua) |
| Trampa de peces | 2 Cmp, 0,5 d, sin energía; ~3 comida/noche (1 tirada/hora, 0 permitido) |
| Procesador de biodiésel | 4 Cmp, 1 d, 2 E/d, 2 agua/d, 4 comida/d → 1 biodiésel/d |
| Extractor de carbón | 8 Cmp + 2 mineral, 1,5 d, 3 E/d → 6 carbón/d; requiere Minería de carbón (4 Cmp, 0,75 d) |
| Extractor de cristales | 10 Cmp + 4 mineral, 2 d, 4 E/d → 2 cristales/d; requiere Cristalografía (10 Cmp + 8 biodiésel, 3 d) |
| Generador eléctrico | 8 Cmp + 2 mineral, 1,5 d, 1 unidad/d → 5/12/20 E/d (madera/carbón/biodiésel); arranca apagado |
| Estación de monitoreo | 6 Cmp, 1,5 d, 2 E/d; pantalla de red |
| Batería | 8 Cmp + 4 mineral, 2 d; +100 cap de energía; requiere Almacenamiento especializado (6 Cmp + 2 mineral, 2 d) |
| Mundo | Default 2048×2048, arrays compactos (~40 MB), generación por anillos difusos |
| Núcleo estable | 2 solar + 2 extractores + invernadero + laboratorio + electrolizador |

El playtest manda. Cualquier cambio se refleja en `config.py` y en [catalogo.md](catalogo.md). El Fabricador queda en **5 Cmp + 2 mineral**; la mina sigue en componentes para no bloquear el arranque.

## Backlog (no agendado)

- Mejoras Mk II, alimañas ambientales, tower defense, botín, inventario y variantes de muerte.
- Desgaste, eventos climáticos, radio y finales.
- UI: 9-slice, autotile y overview solo si el contenido lo pide; las animaciones de menú ya están decididas (D11).
- Splash pre-pygame nativo (framebuffer/CFW) solo si se valida en R36S; el splash actual es pygame temprano.
- UI de construcción: preview de cadena/coste acumulado y feedback de módulo esperando conexión.
- Fichas de construcción/tecnología con efectos numéricos y requisitos; pantalla de Tecnología por ramas/tier.
- Log de eventos (construcción, bloqueo, investigación, reserva crítica) y “cargar último día” en game over.
- Combate/defensa; la trampa de defensa no entra con la trampa de peces.

## No-goals

- Agregar un recurso sin problema, fuente y uso definidos.
- Generalizar un motor de recetas: cada módulo declara su flujo en `module_defs.py`.
- Crear un framework de UI o pantallas con pestañas vacías.
- Combatir/tower defense como próxima etapa.
- Nuitka/PyInstaller para la distribución de consola: sigue siendo PortMaster + squashfs. La beta PC temporal vive aislada en `tools/dev_beta/` y no cambia esa distribución.
- Abrir un slice nuevo antes de cerrar el slice actual.

## Riesgos y decisiones

- **Scope creep:** un slice a la vez; el backlog no se agenda solo.
- **UI:** se mantiene la grilla de 16 px; no crear `ui_state`/`ui_widgets` hasta que haya varias pantallas.
- **Balance:** el loop de chatarra está implementado con números de playtest (26 ruinas, cap 30, reciclador 4 chatarra/d); puede cambiar. El Fabricador cuesta 5 Cmp + 2 mineral.
- **Recursos/costes:** un pool único y `Cost` multi-material. No volver a separar `Stockpile` de `ResourcePool`; los recursos nuevos se agregan al registro con default 0.
- **Save:** `VERSION` 4, sin migración: al cargar un save viejo se borra y se empieza de cero. Guarda un solo bloque `resources`, `stats`, `cost_paid` y `ruinas`. Los IDs de módulos, recursos y tecnologías no se renombran. No hay multisave: la muerte pisa el guardado y el game over persiste al reabrir.
- **Contenido:** módulos y recursos se declaran por datos (flujos, costes, placement y tech); evitar ramas de código por contenido.
- **Documentación:** `plan.md` es el roadmap; `catalogo.md` manda en módulos/tecnologías; `diseno-juego.md` describe el juego; `analisis-temporal.md` fue eliminado el 2026-10-29; este plan es el roadmap vigente.
