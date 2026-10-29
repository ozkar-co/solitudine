# Plan

> Fuente única del roadmap. Catálogo de módulos/tecnologías: [catalogo.md](catalogo.md). Estado: [estado.md](estado.md). Código: [arquitectura.md](arquitectura.md). Juego: [diseno-juego.md](diseno-juego.md).
>
> Regla: un slice a la vez. 4B/4C, la pasada de UI/balance y el playtest están cerrados. Ahora toca la **fundación de recursos/costes** (slice 2). El análisis temporal quedó absorbido acá y en el catálogo/diseño; fue eliminado el 2026-10-29.

## Norte

Gestión y supervivencia en un mapa 2D: red de módulos, recursos, luz y mantenimiento desde la consola del astronauta. La base es jugable y el playtest cerró. El problema inmediato es la **fundación de recursos/costes**; después, cerrar la progresión con chatarra/reciclador, energía y exploración.

## Estado actual (hecho)

- Mapa 1024×1024, cámara, niebla, cables, módulos, buffers, depósitos finitos y muerte por O₂/agua/comida.
- UI 640×480 en grilla de 16 px, sprites, zoom, minimapa, día/noche y lámpara.
- **4B:** laboratorio, investigación de un nodo a la vez, pantalla de Tecnología y desbloqueos.
- **4C:** electrolizador y condensador; O₂ y agua tienen dos fuentes.
- **UI/balance (2026-10-29):**
  - Barra superior con O₂, agua, comida y energía, nombre y `x/y`; mineral/componentes fuera de la barra.
  - Modo recursos (X/C) con los seis recursos, nombre, cap, tendencia y días de los vitales.
  - Menú de construcción con pestañas por categoría, navegación izquierda/derecha, categorías vacías filtradas, bloqueados/no pagables en gris y “Faltan X Cmp”.
  - Panel de módulo con estado real, descripción, producción/consumo con nombre de recurso y día de construcción; buffer, reserva y progreso.
  - Badges de modo/pausa (`RECURSOS`, `CONSTRUIR`, `COLOCAR`, `PAUSA`), celda seleccionada marcada y X disponible en modo colocar.
  - Menú de pausa con Continuar/Créditos; créditos con scroll y easter egg.
  - **Correcciones de playtest (2026-10-29):** hábitat solo con consumo y alertas; recursos sin gasto diario y A vuelve a inspección; construcción con iconos, sin cap de componentes, modal de altura fija con controles al pie y categoría `< >`; estados sin paréntesis.
  - **Tecnología y muerte (2026-10-29):** A otra vez sobre el laboratorio inspeccionado abre Tecnología; SELECT queda libre. La muerte guarda el estado de game over y al reabrir se mantiene.
  - **Arranque (2026-10-29):** splash de texto best-effort en el lanzador antes del runtime; splash con pygame que se mantiene durante assets/guardado/mundo; joystick e inicialización pesada diferidos; al terminar pide START.
  - **Playtest UI (2026-10-29):** red logística única para cualquier módulo; almacén no apagable; menú de construcción con descripción y flujos produce/consume; bloqueos dicen “Investigar”; modales de menú más grandes; Juanka en créditos.
- **Playtest (2026-10-29):** cerrado; los ajustes aplicados quedaron absorbidos por la pasada de UI/balance.
- Guardado `VERSION` 3 (el slice de fundación lo sube a 4); `built_day`, `game_over` y `death_cause` son campos opcionales compatibles con saves viejos. 32 tests de regresión.

## Ahora: fundación de recursos/costes (slice 2)

**Objetivo.** Unificar el modelo de recursos y costes antes de abrir chatarra/reciclador/demolición. Chatarra necesita cantidad y cap propios, costes multi-material, obra que recuerde lo pagado, reembolsos y save v4; hacerlo después obligaría a reescribir el slice 3.

### Alcance

**Entra**

- Registro único de recursos (`ResourceId` + `ResourceDef`) para los seis actuales.
- Pool único de cantidades/caps; `Stockpile` se absorbe y desaparece.
- Coste multi-material (`Cost`) en módulos y tecnologías; pago atómico.
- `Module.cost_paid` persistido y primitiva de reembolso.
- Save `VERSION` 4 con migración v1-v3.
- UI de coste/faltantes con todos los recursos.
- Tests de coste, caps, save y migración.

**No entra**

- Chatarra, ruinas, reciclador, demolición y cancelación de obra jugable (slice 3).
- Batería, trampa de peces, agua RNG/radar, bosques/cristales, biodiésel.
- Rebalanceo general: solo el Fabricador pasa a coste multi-material como caso real.

### Diseño técnico

1. **Registro de recursos (`resources.py`)**
   - `ResourceId`: O2, POWER, WATER, FOOD, MINERAL, COMPONENTS (IDs estables).
   - `ResourceDef`: `id`, `name_key`, `icon`, `base_cap`, `lethal`, `top_bar`, `alert`, `storage_bonus`.
   - `RESOURCES` ordenado para UI; `TOPBAR_IDS`, `ALERT_IDS`, `LETHAL_IDS`.
   - `ResourcePool` pasa a tener los seis montos y los cuatro `*_daily`; `amount`, `add`, `set_amount`, `clamp`.
   - `resources.py` deja de importar `module_defs` (el consumo inicial sale de `config`); esto evita el ciclo `world → resources → module_defs → world`.

2. **Coste (`resources.py`; se elimina `materials.py`)**
   - `Cost` inmutable sobre `dict[ResourceId, float]`; `items()`, `can_afford(pool)`, `spend(pool)`, `missing(pool)`, `refund(pool, ratio, caps)` (acredita hasta el cap y devuelve lo acreditado), `to_dict`/`from_dict`.
   - `spend` atómico: si falta un recurso no descuenta ninguno.
   - `ModuleDef.cost` y `TechDef.cost` pasan de `float` a `Cost`; `CABLE_COST` también.
   - `config.py` guarda los costes como dicts (`COST_FABRICATOR = {"components": 5.0, "mineral": 2.0}`); `module_defs` los convierte a `Cost`.
   - `Simulation.stock` desaparece; todo usa `sim.resources`.

3. **Caps**
   - `network_caps(world) -> dict[ResourceId, float]` desde `ResourceDef.base_cap` + bonus de almacén si `storage_bonus`.
   - `module_tick` y la UI leen caps por `ResourceId`; no hay `NetworkCaps` con campos fijos.
   - El almacén sigue dando +40 a los seis; energía incluida hasta el slice de batería.

4. **Construcción**
   - `kind_cost(kind) -> Cost`; `preview` consulta `pool.can_afford(cost)`; `try_place` descuenta el coste completo y guarda `mod.cost_paid = cost`.
   - `BuildPreview.NO_COMPONENTS` → `NO_RESOURCES`; locale “Recursos insuficientes”.
   - El cable cuesta `CABLE_COST`; no guarda coste por tile (el slice 3 usa el coste fijo del cable).
   - No se agrega todavía cancelar/demoler jugable: la primitiva de reembolso queda testeada para el slice 3.

5. **Save v4**
   - `VERSION = 4`; un solo bloque `sim.resources` con los seis montos + daily; se elimina `sim.stock`.
   - `world.modules[].cost_paid` como dict `{resource_id: amount}`; `built_day` sigue opcional.
   - Migración v1-v3: signo de daily, fusionar `stock` en `resources`, inferir `cost_paid` con el coste actual del módulo (save de desarrollo; no se preserva el coste histórico exacto).
   - Loader tolerante: recursos nuevos ausentes → 0.0 (prepara chatarra en v4 sin romper saves).
   - El `save.json` actual v3 debe cargar y migrar.

6. **UI**
   - Barra superior y modo recursos salen del registro; no listas hardcodeadas.
   - Menú de construcción: coste con un icono+cantidad por recurso; “Faltan …” por recurso; gris si falta cualquiera.
   - Panel de colocar: coste completo con iconos; el panel de 192 px debe entrar en una fila de dos recursos o dos líneas.
   - Tecnología: coste con nombres cortos (`Cmp`, `Min`) hasta que la pantalla se rediseñe con iconos.
   - Añadir `resource.*.short` y ajustar `build.missing`/`build.err.no_resources`.

### Tabla de costes del slice

| Módulo | Coste v4 |
|--------|----------|
| Cable | 1 Cmp |
| Panel solar | 5 Cmp |
| Extractor | 6 Cmp |
| Mina | 4 Cmp |
| Invernadero | 8 Cmp |
| Fabricador | **5 Cmp + 2 mineral** |
| Almacén | 5 Cmp |
| Radar | 8 Cmp |
| Lámpara | 6 Cmp |
| Laboratorio | 8 Cmp |
| Electrolizador | 6 Cmp |
| Condensador | 8 Cmp |
| Investigación T1 | 4 Cmp |

La mina queda solo en componentes para no bloquear el arranque: es la fuente de mineral. El Fabricador es el caso real de coste multi-material; el resto conserva sus números de playtest. La tabla se refleja en [catalogo.md](catalogo.md) antes de tocar código.

### Pasos

1. Docs + tabla de costes + tests base (sin cambiar comportamiento).
2. Registro/pool único y caps por `ResourceId`; adaptar tick, logística y UI a `sim.resources`; tests verdes.
3. `Cost` + costes de módulos/tecnologías + construcción/research; test de pago atómico.
4. `Module.cost_paid` + save v4 + migración + tests de roundtrip v3→v4.
5. UI de coste multi-material y faltantes; revisar 640×480.
6. `make test`, cargar el `save.json` actual, playtest corto del Fabricador y del menú.

### Criterio de cierre

- Un módulo actual (Fabricador) declara y cobra dos recursos; el pago es atómico.
- La obra guarda `cost_paid` y sobrevive a guardar/cargar.
- Save v4 carga v1-v3 sin pérdida de recursos.
- La UI muestra todos los costes y faltantes; no hay texto cortado a 640×480.
- `make test` pasa con los 32 tests actuales adaptados + tests nuevos.
- Sin softlock: la mina sigue siendo construible solo con componentes.
- Chatarra/reciclador/demolición quedan explícitamente fuera.

## Decisiones cerradas

### Recursos

- La regla de **2 fuentes / 2 usos** es una heurística, no una regla estricta. Se acepta una excepción si resuelve un problema claro y no deja un recurso de un solo uso.
- Recursos actuales: O₂, agua, comida, energía, mineral y componentes.
- Recursos planificados: **chatarra** (intermedio), **madera/biomasa**, **cristal** y **biodiésel** (producido, no extraído).
- La matriz completa vive en este plan; el catálogo define módulos/tecnologías.

### Chatarra, ruinas y reciclador

- La chatarra entra a la red, tiene cap propio menor que los recursos normales y el almacén lo amplía. Se muestra en modo recursos.
- Se recoge de ruinas desde el día 0; el monto es variable y queda guardado en cada ruina.
- Ruinas: 1 tile, 2 garantizadas y el resto procedurales; solo en zonas abiertas sin agua/mineral/árboles/cristales; bloquean construcción y cables; se guardan.
- Demoler un módulo crea una ruina de su tamaño (hoy 1×1). La recogida es instantánea y sin coste.
- Demolición disponible desde el día 0 con confirmación; devuelve 0,6-0,9 del equivalente mineral del módulo. El cable devuelve sus componentes íntegros (caso especial).
- Cancelar una obra devuelve chatarra equivalente al progreso, con cap 0,9; los materiales extra no componentes se pierden.
- Reciclador: requiere tecnología; coste propuesto 2-3 Cmp, 0,5 día, 1 E/d y 0,5 agua/d (asumido); convierte chatarra en mineral con ratio 0,9; trazas raras de otros materiales; registra chatarra procesada y producida.
- Investigación del reciclador: 5 chatarra + 2 Cmp + 1 mineral. El árbol de tecnologías se armará por etapas; el motor debe soportarlo desde el principio.
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
- Modo recursos: seis recursos con cantidad/cap; sin gasto diario ni días. A inspecciona y vuelve al terreno.
- Panel del hábitat: solo consumo diario por vital y alertas; las cantidades/caps viven en modo recursos.
- Menú de construcción por pestañas; categorías vacías ocultas; no disponibles en gris con “Investigar”; coste, faltante, descripción y flujo produce/consume visibles. Recursos con iconos y sin cap de componentes; el coste muestra icono y cantidad del recurso entre paréntesis; modal amplio de altura fija con controles en pie separado; categoría seleccionada resaltada y entre `< >`.
- Panel de módulo: estado, descripción, producción/consumo con nombres y día de construcción. Los módulos mixtos muestran ambas cosas.
- Acciones especiales: cada módulo declara `special_action`; con el módulo activo e inspeccionado, A ejecuta la acción y el panel muestra “Pulsa A para {acción}”. SELECT queda libre. Laboratorio: A otra vez abre Tecnología. El cable forma una red logística única que conecta módulos de cualquier tipo; el almacén no se puede apagar.
- Badge de modo/pausa y celda seleccionada. X cambia capa también en modo colocar. Los estados son concisos, sin paréntesis explicativos.
- Sin menú de ayuda dedicado: la UI debe ser autoexplicativa; se mantienen los hints contextuales.
- Créditos en pausa con scroll y easter egg sin pistas.

## Orden de implementación

1. ~~Playtest y correcciones.~~ Cerrado (2026-10-29).
2. **Fundación de recursos/costes (actual).** Detalle en “Ahora”. Criterio: un módulo actual declara varios costes y la obra se guarda/carga. La tabla de costes vive en [catalogo.md](catalogo.md).
3. **Chatarra/reciclador/demolición.** Primer slice de contenido nuevo; incluye el nodo de tecnología del reciclador. Criterio: recoger, reciclar, demoler, guardar y balancear el loop.
4. **Trampa de peces + comida.** Criterio: placement sobre agua, cable sobre agua, producción nocturna y parada al agotarse el agua.
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
| Comida | Invernadero; trampa de peces (planificada) | Soporte vital; biodiésel y fabricación de trampas (planificado) | Hecho / planificado |
| Mineral | Mina; reciclador (planificado) | Fabricador | Hecho / planificado |
| Componentes | Fabricador | Construcción, investigación | Hecho |
| Chatarra | Ruinas, demolición | Reciclador, investigación | Planificado |
| Madera/biomasa | Bosques | Módulos/consumibles por definir | Planificado |
| Cristal | Depósitos subterráneos | Tecnología/módulos avanzados por definir | Planificado |
| Biodiésel | Producción (módulo por definir) | Energía/consumibles por definir | Planificado |

> 2 fuentes / 2 usos es deseable, no obligatorio. No se agrega un recurso sin un problema que resuelva y al menos una fuente y un uso definidos.

## Números actuales (playtest)

| Parámetro | Valor |
|-----------|-------|
| Reservas iniciales | 12 O₂ / 9 agua / 7 comida / 10 energía (días) |
| Caps iniciales | 140 O₂ / 100 agua / 80 comida / 100 energía |
| Componentes iniciales / cap | 60 / 80 |
| Laboratorio | 8 Cmp, 1,5 d, 3 E/d |
| Investigación T1 | 4 Cmp, 1,5 d |
| Electrolizador | 6 Cmp, 1 d, 4 E/d, 6 agua/d → 8 O₂/d |
| Condensador | 8 Cmp, 1,5 d, 6 E/d → 8 agua/d |
| Radar | 8 Cmp, 1,5 d, 12 E/d |
| Invernadero | 8 Cmp, 1,5 d, 3 E/d, 4 agua/d → 10 comida/d + 2 O₂/d (O₂ requiere agua) |
| Núcleo estable | 2 solar + 2 extractores + invernadero + laboratorio + electrolizador |

El playtest manda. Cualquier cambio se refleja en `config.py` y en [catalogo.md](catalogo.md). En el slice de fundación, el Fabricador pasa a **5 Cmp + 2 mineral**; la mina sigue en componentes para no bloquear el arranque.

## Backlog (no agendado)

- Mejoras Mk II, alimañas ambientales, tower defense, botín, inventario y variantes de muerte.
- Desgaste, eventos climáticos, radio y finales.
- UI: 9-slice, autotile, animaciones y overview solo si el contenido lo pide.
- Splash pre-pygame nativo (framebuffer/CFW) solo si se valida en R36S; el splash actual es pygame temprano.
- UI de construcción: preview de cadena/coste acumulado, B borra cable y feedback de módulo esperando conexión.
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
- **Balance:** los números actuales son propuestas de playtest; pueden cambiar. La fundación solo cambia el coste del Fabricador; el resto se mantiene.
- **Recursos/costes:** un pool único y `Cost` multi-material. No volver a separar `Stockpile` de `ResourcePool`; los recursos nuevos se agregan al registro con default 0.
- **Save:** `VERSION` 4 en este slice, con migración v1-v3, un solo bloque `resources` y `cost_paid` por obra. Los IDs de módulos, recursos y tecnologías no se renombran. No hay multisave: la muerte pisa el guardado y el game over persiste al reabrir.
- **Contenido:** módulos y recursos se declaran por datos (flujos, costes, placement y tech); evitar ramas de código por contenido.
- **Documentación:** `plan.md` es el roadmap; `catalogo.md` manda en módulos/tecnologías; `diseno-juego.md` describe el juego; `analisis-temporal.md` fue eliminado el 2026-10-29; este plan es el roadmap vigente.
