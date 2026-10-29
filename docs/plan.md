# Plan

> Fuente única del roadmap. Catálogo de módulos/tecnologías: [catalogo.md](catalogo.md). Estado: [estado.md](estado.md). Código: [arquitectura.md](arquitectura.md). Juego: [diseno-juego.md](diseno-juego.md).
>
> Regla: un slice a la vez. 4B/4C, UI/balance, playtest, fundación de recursos/costes y chatarra/reciclador/demolición están cerrados. Ahora toca la **trampa de peces + comida** (slice 4). El análisis temporal quedó absorbido acá y en el catálogo/diseño; fue eliminado el 2026-10-29.

## Norte

Gestión y supervivencia en un mapa 2D: red de módulos, recursos, luz y mantenimiento desde la consola del astronauta. La base es jugable, el playtest cerró y el loop de chatarra/reciclador ya está implementado. El problema inmediato es la **comida recurrente** (trampa de peces); después, energía y exploración.

## Estado actual (hecho)

- Mapa 1024×1024, cámara, niebla, cables, módulos, buffers, depósitos finitos y muerte por O₂/agua/comida.
- UI 640×480 en grilla de 16 px, sprites, zoom, minimapa, día/noche y lámpara.
- **4B:** laboratorio, investigación de un nodo a la vez, pantalla de Tecnología y desbloqueos.
- **4C:** electrolizador y condensador; O₂ y agua tienen dos fuentes.
- **UI/balance (2026-10-29):**
  - Barra superior con O₂, agua, comida y energía, nombre y `x/y`; mineral/componentes fuera de la barra.
  - Modo recursos (X/C) con los siete recursos, nombre, cap, tendencia y días de los vitales.
  - Menú de construcción con pestañas por categoría, navegación izquierda/derecha, categorías vacías filtradas, bloqueados/no pagables en gris y faltantes por recurso.
  - Panel de módulo con estado real, descripción, producción/consumo con nombre de recurso y día de construcción; buffer, reserva y progreso.
  - Badges de modo/pausa (`RECURSOS`, `CONSTRUIR`, `COLOCAR`, `PAUSA`), celda seleccionada marcada y X disponible en modo colocar.
  - Menú de pausa con Continuar/Créditos; créditos con scroll y easter egg.
  - **Correcciones de playtest (2026-10-29):** hábitat solo con consumo y alertas; recursos sin gasto diario y A vuelve a inspección; construcción con iconos, sin cap de componentes, modal de altura fija con controles al pie y categoría `< >`; estados sin paréntesis.
  - **Tecnología y muerte (2026-10-29):** A otra vez sobre el laboratorio inspeccionado abre Tecnología; SELECT queda libre. La muerte guarda el estado de game over y al reabrir se mantiene.
  - **Arranque (2026-10-29):** splash de texto best-effort en el lanzador antes del runtime; splash con pygame que se mantiene durante assets/guardado/mundo; joystick e inicialización pesada diferidos; al terminar pide START.
  - **Playtest UI (2026-10-29):** red logística única para cualquier módulo; almacén no apagable; menú de construcción con descripción y flujos produce/consume; bloqueos dicen “Investigar”; modales de menú más grandes; Juanka en créditos.
- **Playtest (2026-10-29):** cerrado; los ajustes aplicados quedaron absorbidos por la pasada de UI/balance.
- Guardado `VERSION` 4; sin migración (los saves viejos se borran). 49 tests de regresión.

## Hecho: fundación de recursos/costes + chatarra (2026-10-29)

**Fundación**

- Pool único con siete recursos (O₂, agua, comida, energía, mineral, componentes y chatarra); `ResourceId`/`ResourceDef` y caps por recurso.
- `Cost` multi-material con pago atómico, `missing`, reembolso y `Module.cost_paid`.
- Fabricador: **5 Cmp + 2 mineral**; la mina sigue solo con componentes para no bloquear el arranque.
- Save `VERSION` 4 **sin migración**: al cargar un save viejo se borra y se empieza de cero.
- UI: coste con iconos/cantidades, faltantes por recurso; barra superior y modo recursos desde el registro.

**Chatarra, ruinas y reciclador**

- 26 ruinas (2 garantizadas cerca del hábitat, 24 procedurales), 1 tile y 4-10 chatarra; bloquean construcción y cable.
- Recogida instantánea con **A**; cap de chatarra 30 (+40 por almacén); el remanente queda guardado.
- **Demolición:** con un módulo o cable seleccionado, **B** abre confirmación y **A** demuele. Un módulo deja una ruina con 0,6-0,9 del equivalente mineral; el cable devuelve 1 Cmp.
- **Cancelar obra:** componentes pagados × `min(progreso, 0,9)` en chatarra; el resto de materiales se pierde.
- **Reciclador:** 3 Cmp, 0,5 d, 1 E/d, 0,5 agua/d; 4 chatarra/d → 3,6 mineral/d + 0,2 Cmp/d; registra chatarra procesada y mineral reciclado.
- **Tecnología `reciclaje`:** T1 provisional (el árbol T2 se armará después), 5 chatarra + 2 Cmp + 1 mineral, 2 d; requiere laboratorio.
- 49 tests de regresión; `make test` verde.

## Ahora: trampa de peces + comida (slice 4)

- Módulo `fish_trap`: 1-2 Cmp, placement sobre agua, cable sobre agua, sin energía; 1-2 comida/noche.
- Se detiene si el agua se agota; demoler devuelve chatarra.
- Criterio: placement sobre agua, cable sobre agua, producción nocturna, parada al agotarse el agua y guardado.
- No entra la trampa de defensa.

## Decisiones cerradas

### Recursos

- La regla de **2 fuentes / 2 usos** es una heurística, no una regla estricta. Se acepta una excepción si resuelve un problema claro y no deja un recurso de un solo uso.
- Recursos actuales: O₂, agua, comida, energía, mineral, componentes y **chatarra**.
- Recursos planificados: **madera/biomasa**, **cristal** y **biodiésel** (producido, no extraído).
- La matriz completa vive en este plan; el catálogo define módulos/tecnologías.

### Chatarra, ruinas y reciclador

- La chatarra entra a la red, tiene cap propio de **30** (+40 por almacén) y se muestra en modo recursos.
- Se recoge de ruinas desde el día 0 con **A**; el monto es variable (4-10) y el remanente queda guardado.
- Ruinas: **26** (2 garantizadas cerca del hábitat, 24 procedurales), 1 tile; solo en zonas abiertas sin agua/mineral/árboles/cristales; bloquean construcción y cables; se guardan.
- Demoler un módulo crea una ruina de su tamaño (hoy 1×1). La recogida es instantánea y sin coste.
- Demolición con **B** sobre el módulo/cable seleccionado y confirmación con **A**; el módulo deja una ruina con 0,6-0,9 del equivalente mineral. El cable devuelve 1 Cmp íntegro.
- Cancelar una obra devuelve chatarra equivalente a los componentes pagados × `min(progreso, 0,9)`; los materiales extra no componentes se pierden.
- Reciclador: 3 Cmp, 0,5 día, 1 E/d y 0,5 agua/d; 4 chatarra/d → 3,6 mineral/d + 0,2 Cmp/d; registra chatarra procesada y mineral reciclado.
- Investigación `reciclaje`: T1 provisional (el árbol T2 se armará después), 5 chatarra + 2 Cmp + 1 mineral, 2 días; requiere laboratorio.
- No vuelve obsoleta a la mina: la chatarra es limitada, RNG y menos abundante; cierra el ciclo de lo construido y da una segunda fuente de mineral.

### Comida, trampas y biodiésel

- La comida es un problema recurrente. Se gastará en fabricar biodiésel y en la fabricación de trampas.
- **Trampa de peces** (inicial): 1-2 Cmp; se coloca sobre agua y se conecta a la red aunque no consuma energía; produce 1-2 comida por noche; no es fuente primaria salvo en cantidad; si el agua se agota, queda inútil para siempre y se puede demoler para recuperar chatarra.
- El cable puede ir sobre agua. La trampa es un módulo aparte y no comparte tile con el extractor.
- La **trampa de defensa** queda para cuando exista combate.
- **Biodiésel:** recurso producido, no extraído; su módulo/productor y consumidor se definirán más adelante. Cuando dos módulos o la supervivencia compiten por un recurso, el jugador controla apagando módulos; el reparto es igualitario y los empates se resuelven al azar.

### Agua y exploración

- El agua tiene un depósito garantizado; se agregarán depósitos RNG. Es finita y no se regenera.
- El radar es la única exploración permanente y encuentra todo (incluidos ruinas, bosques y cristales).
- Quedarse sin energía puede matar por sed a través del condensador; se acepta.
- Cuando un depósito se agota, el tile vuelve a suelo; extractor y trampa quedan inútiles.

### Energía

- La **batería** es capacidad de energía; el almacén deja de aumentar el cap de energía.
- El hábitat tiene un cap inicial de energía; la batería solo aumenta cap (el excedente diurno ya se almacena con la funcionalidad actual).
- La batería queda detrás de investigación (T2). A medida que existan tanques especializados podrían quitarse capacidades al almacén; por ahora solo la batería.
- El almacén sigue dando +40 a los recursos que no tengan reservorio especializado.

### Bosques y cristales

- Son contenido base, no DLC; su implementación debe servir para probar la creación parametrizable de recursos para un DLC.
- Bosques renovables: dejan brotes en el suelo y tardan varios meses de juego en regrow; bloquean construcción.
- Cristales finitos, solo bajo tierra; se definen más adelante junto con su extractor.
- No se agregan hasta tener al menos un uso concreto para cada uno; pueden aparecer como scenery inerte antes, pero sin confundir al jugador.

### UI

- Barra superior solo con los cuatro vitales, con nombres; si no caben, se decide en playtest.
- Modo recursos: siete recursos con cantidad/cap; sin gasto diario ni días. A inspecciona y vuelve al terreno.
- Panel del hábitat: solo consumo diario por vital y alertas; las cantidades/caps viven en modo recursos.
- Menú de construcción por pestañas; categorías vacías ocultas; no disponibles en gris con “Investigar”; coste, faltante, descripción y flujo produce/consume visibles. Coste multi-material con un icono+cantidad por recurso y faltantes por recurso; modal amplio de altura fija con controles en pie separado; categoría seleccionada resaltada y entre `< >`.
- Panel de módulo: estado, descripción, producción/consumo con nombres y día de construcción. Los módulos mixtos muestran ambas cosas; el reciclador muestra chatarra procesada y mineral reciclado.
- Ruinas: se dibujan en el mapa, se inspeccionan en el panel y se recogen con A. La demolición/cancelación abre un modal con confirmación A/B.
- Acciones especiales: cada módulo declara `special_action`; con el módulo activo e inspeccionado, A ejecuta la acción y el panel muestra “Pulsa A para {acción}”. SELECT queda libre. Laboratorio: A otra vez abre Tecnología. El cable forma una red logística única que conecta módulos de cualquier tipo; el almacén no se puede apagar.
- Badge de modo/pausa y celda seleccionada. X cambia capa también en modo colocar. Los estados son concisos, sin paréntesis explicativos.
- Sin menú de ayuda dedicado: la UI debe ser autoexplicativa; se mantienen los hints contextuales.
- Créditos en pausa con scroll y easter egg sin pistas.

## Orden de implementación

1. ~~Playtest y correcciones.~~ Cerrado (2026-10-29).
2. ~~Fundación de recursos/costes.~~ Cerrado (2026-10-29).
3. ~~Chatarra/reciclador/demolición.~~ Cerrado (2026-10-29).
4. **Trampa de peces + comida (actual).** Criterio: placement sobre agua, cable sobre agua, producción nocturna y parada al agotarse el agua.
5. **Batería/almacén + energía.** Criterio: almacén sin cap de energía, batería con cap, tecnología y rebalance.
6. **Agua RNG + radar.** Criterio: depósito garantizado + aleatorios, radar relevante, avisos y sin softlock.
7. **Bosques/cristales/biodiésel.** Criterio: al menos un uso concreto por recurso y paso por el estándar de recursos.
8. **Eventos, expansión y combate.** Backlog; no abrir antes de cerrar los slices anteriores.

## Matriz de recursos

| Recurso | Fuentes | Usos | Estado |
|---------|---------|------|--------|
| O₂ | Reserva inicial, invernadero (con agua), electrolizador | Soporte vital | Hecho |
| Agua | Extractor, condensador | Soporte vital, invernadero, electrólisis | Hecho |
| Energía | Panel solar | Casi todos los módulos | Hecho |
| Comida | Invernadero; trampa de peces (planificada) | Soporte vital; biodiésel y fabricación de trampas (planificado) | Hecho / trampa planificada |
| Mineral | Mina; reciclador | Fabricador | Hecho |
| Componentes | Fabricador | Construcción, investigación | Hecho |
| Chatarra | Ruinas, demolición | Reciclador, investigación | Hecho |
| Madera/biomasa | Bosques | Módulos/consumibles por definir | Planificado |
| Cristal | Depósitos subterráneos | Tecnología/módulos avanzados por definir | Planificado |
| Biodiésel | Producción (módulo por definir) | Energía/consumibles por definir | Planificado |

> 2 fuentes / 2 usos es deseable, no obligatorio. No se agrega un recurso sin un problema que resuelva y al menos una fuente y un uso definidos.

## Números actuales

| Parámetro | Valor |
|-----------|-------|
| Reservas iniciales | 12 O₂ / 9 agua / 7 comida / 10 energía (días) |
| Caps iniciales | 140 O₂ / 100 agua / 80 comida / 100 energía / 40 mineral / 80 Cmp / 30 chatarra |
| Componentes iniciales / cap | 60 / 80 |
| Chatarra inicial / cap | 0 / 30 (+40 por almacén) |
| Ruinas | 26 (2 garantizadas + 24 procedurales), 4-10 chatarra |
| Fabricador | 5 Cmp + 2 mineral, 2 d, 4 E/d, 6 mineral/d → 4 Cmp/d |
| Reciclador | 3 Cmp, 0,5 d, 1 E/d, 0,5 agua/d, 4 chatarra/d → 3,6 mineral/d + 0,2 Cmp/d |
| Investigación `reciclaje` | 5 chatarra + 2 Cmp + 1 mineral, 2 d (T1 provisional) |
| Laboratorio | 8 Cmp, 1,5 d, 3 E/d |
| Investigación T1 | 4 Cmp, 1,5 d |
| Electrolizador | 6 Cmp, 1 d, 4 E/d, 6 agua/d → 8 O₂/d |
| Condensador | 8 Cmp, 1,5 d, 6 E/d → 8 agua/d |
| Radar | 8 Cmp, 1,5 d, 12 E/d |
| Invernadero | 8 Cmp, 1,5 d, 3 E/d, 4 agua/d → 10 comida/d + 2 O₂/d (O₂ requiere agua) |
| Núcleo estable | 2 solar + 2 extractores + invernadero + laboratorio + electrolizador |

El playtest manda. Cualquier cambio se refleja en `config.py` y en [catalogo.md](catalogo.md). El Fabricador queda en **5 Cmp + 2 mineral**; la mina sigue en componentes para no bloquear el arranque.

## Backlog (no agendado)

- Mejoras Mk II, alimañas ambientales, tower defense, botín, inventario y variantes de muerte.
- Desgaste, eventos climáticos, radio y finales.
- UI: 9-slice, autotile, animaciones y overview solo si el contenido lo pide.
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
- Nuitka/PyInstaller: la distribución sigue siendo PortMaster + squashfs.
- Abrir un slice nuevo antes de cerrar el slice actual.

## Riesgos y decisiones

- **Scope creep:** un slice a la vez; el backlog no se agenda solo.
- **UI:** se mantiene la grilla de 16 px; no crear `ui_state`/`ui_widgets` hasta que haya varias pantallas.
- **Balance:** el loop de chatarra está implementado con números de playtest (26 ruinas, cap 30, reciclador 4 chatarra/d); puede cambiar. El Fabricador cuesta 5 Cmp + 2 mineral.
- **Recursos/costes:** un pool único y `Cost` multi-material. No volver a separar `Stockpile` de `ResourcePool`; los recursos nuevos se agregan al registro con default 0.
- **Save:** `VERSION` 4, sin migración: al cargar un save viejo se borra y se empieza de cero. Guarda un solo bloque `resources`, `stats`, `cost_paid` y `ruinas`. Los IDs de módulos, recursos y tecnologías no se renombran. No hay multisave: la muerte pisa el guardado y el game over persiste al reabrir.
- **Contenido:** módulos y recursos se declaran por datos (flujos, costes, placement y tech); evitar ramas de código por contenido.
- **Documentación:** `plan.md` es el roadmap; `catalogo.md` manda en módulos/tecnologías; `diseno-juego.md` describe el juego; `analisis-temporal.md` fue eliminado el 2026-10-29; este plan es el roadmap vigente.
