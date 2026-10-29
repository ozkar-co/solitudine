# Análisis temporal (documento de trabajo)

> **No es fuente de verdad.** Es un documento temporal para analizar decisiones antes de seguir agregando contenido. No actualizar `plan.md`, `catalogo.md` ni `diseno-juego.md` desde acá. Borrar o mover cuando las decisiones estén tomadas.

## Implementado en esta pasada (info real)

- Días restantes y alertas usan el **cambio neto real** de cada recurso, no el consumo bruto del hábitat.
- La barra superior muestra **x/y** de los seis recursos: O2, agua, comida, energía, mineral y componentes.
- El panel del hábitat muestra **x/y + tendencia/día + días restantes**.
- El panel de módulo ya no muestra los flujos diarios nominales. Muestra un **estado real** (sin agua, sin mineral, sin salida, sin energía, depósito agotado, O2 lleno, noche, etc.).
- Los flujos diarios nominales pasaron al **overlay de debug** (`--dev`), solo para el módulo seleccionado.
- El **menú de construcción** y el **modo colocar** pausan el tiempo. La partida no arranca pausada.
- Un extractor/mina con depósito agotado ya **no consume energía**.
- Guardado: `VERSION` 3; los guardados v1/v2 con tasas positivas se convierten a netas negativas al cargar.
- Tests nuevos: días netos y extractor agotado sin consumo.

---

## Balance actual (medido con el código previo a esta pasada)

| Escenario | Resultado |
|-----------|-----------|
| No construir nada | Muerte día **5.99** (comida) |
| Solar + extractor + invernadero (19 Cmp) | Muerte por O2 día **7.12** |
| + laboratorio + investigación (35 Cmp) | Investigación OK, quedan **7 Cmp**; electrolizador cuesta **8**; muerte O2 7.12 |
| + mina + fabricador + lab + investigación + electrolizador | Electrolizador a medio construir; energía 0 el día 6; muerte O2 6.96 |

Conclusiones:

- **6 días = 4:48 reales** a 48 s/día. El margen inicial es demasiado corto para leer, probar y equivocarse.
- El paquete mínimo de supervivencia compra apenas **~1 día** de O2.
- El 4C es un callejón sin salida: se desbloquea el electrolizador y no alcanzan los componentes para construirlo.
- El invernadero resuelve comida (10 vs 8) y aporta O2; el electrolizador (4 O2/día) no compite.
- El invernadero produce O2 **sin agua** por el orden del tick. Si la idea es que el O2 sea residual, hay que corregir también esa dependencia.
- El condensador (5 agua/6 energía) es peor que el extractor (12 agua/2 energía) y el agua sobra. No tiene problema que resolver.
- La energía es una restricción invisible: un módulo puede estar “en línea” y producir 0.
- El radar cuesta 10 Cmp + 24 E/día y no hay nada que encontrar: los recursos iniciales están a 2-5 tiles.
- La lámpara cuesta 6 Cmp + 4 E/noche y es cosmética.
- Storage ya da +40 de capacidad de energía; una batería separada es redundante hasta definir la diferencia.

### Hipótesis de números para playtest (no implementado)

| Parámetro | Actual | Hipótesis |
|-----------|--------|-----------|
| Inicio O2/agua/comida/energía | 6/6/6/6 días | 12/9/7/10 días escalonados |
| Caps iniciales | 80/60/50/80 | 140/100/80/100 |
| Cmp iniciales / cap | 42/50 | 60-70 / 80-100 |
| Laboratorio | 10 Cmp, 2 d | 8 Cmp, 1.5 d |
| Investigación T1 | 6 Cmp, 2 d | 4-5 Cmp, 1.5 d |
| Electrolizador | 4 O2, 6 agua, 4 E, 8 Cmp, 1.5 d | 8 O2, 6 agua, 4 E, 6 Cmp, 1 d |
| Invernadero | 10 comida, 2 O2, 4 agua, 3 E | Igual, pero O2 residual y dependiente de agua |
| Condensador | 5 agua, 6 E, 8 Cmp | 8-10 agua, 6 E, 8 Cmp; o diferir |
| Radar | 10 Cmp, 24 E/día | 8 Cmp, 8-12 E/día; o una pasada de escaneo |

Núcleo estable objetivo: 2 solares + 2 extractores + 1 invernadero + 1 laboratorio + 1 electrolizador. Con 8 O2/día del electrolizador, el O2 queda en break-even y el agua/energía se vuelven decisiones. Coste aproximado: 48-54 Cmp + cables.

---

## UX: hallazgos para analizar

Prioridad alta:

- **Pausa del menú de construcción y del modo colocar** (implementado): el tiempo ya no corre mientras el jugador lee o elige un tile. La partida no arranca pausada. Falta un indicador visible de “PAUSA” en esos modos.
- **Hacer visible el modo.** No hay badge persistente de MODO, no se marca el tile seleccionado y el cursor siempre es igual. A cambia de significado según el modo.
- **Estado real del módulo** (implementado en parte): falta que la UI explique mejor el motivo y las acciones disponibles.
- **Iconos sin leyenda.** No hay forma de saber qué representa cada icono. Opciones: menú de ayuda; que el “modo recursos” muestre la lista de recursos con icono y nombre; nombres también en fichas y paneles.
- **Barra superior solo con recursos vitales.** Mostrar solo O2, agua, comida y energía; mineral y componentes pasan a un modo/panel secundario. La barra no puede crecer sin límite.
- **Menú de construcción con pestañas.** Las categorías deben ser pestañas; los módulos no disponibles se muestran en gris con el motivo, no se ocultan.
- **Panel del módulo: solo producción.** Al analizar un módulo, mostrar solo la producción (así cada flujo entra con el nombre del recurso), no el detalle de todos los flujos.
- **Cancelar obra / demoler.** Un clic malo cuesta 8-10 Cmp y 1.5-2 días para siempre. Cancelar obra debería reembolsar; demoler debería existir desde el inicio con reembolso parcial, no detrás de “reciclaje”.
- **Cable vs módulo.** El cable es trazo continuo y el módulo es de a uno. No se comunica. El cable queda en modo colocar; el módulo sale solo. No hay preview de la cadena ni coste acumulado. B sale pero no borra. Un módulo puede decir “válida” sin conexión y quedarse esperando sin construirse.
- **Capa X** no funciona en modo colocar; la capa no cambia el preview. Para buscar un depósito hay que salir, cambiar capa y volver a entrar.
- **Ayuda contextual**: hoy muestra R1 aunque el tile sea cable/suelo; no muestra B=cancelar/demoler. Debe depender del objeto seleccionado.
- **Fichas de construcción y tecnología** con efectos numéricos y requisitos. Hoy solo hay nombre, coste y bloqueo; no se puede comparar electrolizador vs invernadero antes de gastar.
- **Flujos diarios**: pasaron a debug. Si se quiere una vista dedicada, hacer un panel de red/consumo más adelante, no saturar el panel del módulo.

Prioridad media:

- Log/eventos: construcción terminada, módulo bloqueado, investigación completada, reserva crítica. Ayuda a entender la muerte.
- Barra superior: validar en R36S la legibilidad con solo los recursos vitales.
- Menú de construcción: mostrar “faltan X Cmp” y marcar costes no pagables dentro de cada pestaña.
- Pantalla de tecnología: mostrar ramas, tier y efecto del módulo; el listado plano no escala.
- Guardado/reintento: ofrecer “cargar último día” en game over (el autoguardado ya existe).
- Nombres/acentos consistentes (“Energia/Energía”, “Modulo/Módulo”).

---

## Ideas y decisiones pendientes

### Chatarra y reciclador

> Actualizado 2026-10-29 con las respuestas. El detalle y las preguntas nuevas están en “Reanálisis contra catálogo, diseño y plan”.

- La chatarra es un **recurso nuevo intermedio** (no vital): se convierte en mineral y se gasta en algunas investigaciones.
- El inicio tiene **chatarra/ruinas procedurales** alrededor del hábitat; demoler módulos también puede producir chatarra.
- El **reciclador** es barato y complementa a la mina/fabricador; convierte chatarra en mineral.
- Pendiente: si el reciclador requiere tecnología o está desde el inicio; ratio, tiempo y energía; si la demolición se desbloquea desde el inicio o con `reciclaje`; cómo se recoge y se guarda; y cómo se resuelve la regla de la matriz de recursos.

### Nuevos recursos y módulos

> Actualizado 2026-10-29: bosques y cristales son **base**, no DLC. Su implementación debe servir para probar la creación parametrizable de recursos para un DLC. El mapa sigue en 1024×1024.

- **Bosques**: recurso nuevo (biomasa/madera) con un módulo extractor que trabaja sobre un 3×3, similar a extractor/mina.
- **Cristales subterráneos**: recurso escaso, requiere exploración; se usa en tecnologías especializadas o contenido futuro.
- Preguntas:
  - ¿Qué problema del jugador resuelve cada recurso? No agregar contenido sin una necesidad sentida.
  - ¿Cuántas fuentes y usos tiene cada recurso? Mantener la regla de la matriz.
  - ¿Los bosques son renovables? ¿Se agotan? ¿Se pueden replantar?
  - ¿Los cristales son finitos y obligan a explorar? ¿El radar los revela?
  - ¿Qué módulo extrae cada uno y qué requisito de colocación tiene?
  - ¿Afectan el balance base o son contenido opcional/DLC?

### Base escalable / DLC

- `module_defs.py` y `catalogo.md` deben seguir siendo la fuente única.
- IDs estables para módulos, recursos y tecnologías; no renombrar IDs guardados.
- Recursos y módulos declarativos (flujos, costes, placement, tech) para agregar contenido sin tocar el tick.
- Validar la matriz de recursos (fuentes/usos) antes de sumar un recurso.
- Separar contenido base de contenido opcional (DLC/futuro) por datos/flags, no por ramas de código.
- Guardado versionado y migraciones por versión.
- UI escalable: categorías del menú, scroll o segundo nivel; pantalla de tecnología con ramas; no listas planas infinitas.
- Assets y localización por ID; no hardcodear textos.
- Definir qué recursos son “vitales” y cuáles “industriales”; la barra superior no puede crecer sin límite.

### Comida

> Actualizado 2026-10-29: la comida es recurrente y tiene nuevos sinks (fabricar biodiésel y fabricar trampas). La segunda fuente ya no es solo una alternativa: puede ser necesaria para cubrir esos consumos.

- Hoy un invernadero resuelve la comida. Una segunda fuente solo tiene sentido si crea una elección.
- Idea: **trampa de peces** barata (4 Cmp, 1 día, +5 comida, sin agua/energía, junto a agua, una por parche). Rol: comida temprana o comida sin agua; el invernadero queda como mejora.
- Si no se quiere una segunda fuente, no agregarla: sería contenido redundante.

### Exploración y mapa

> Actualizado 2026-10-29: el mapa sigue en 1024×1024, pero el agua puede depender de RNG/agotarse. Eso puede darle al radar un rol real; falta decidir si hay un depósito inicial garantizado.

- Los recursos iniciales están a 2-5 tiles; el radar es caro y no hay botín/POI. La exploración no tiene payoff económico.
- Opciones:
  1. Hacer escasos los depósitos locales, reducir el coste/consumo del radar y agregar un aviso “depósito encontrado”. Así el radar y la expansión tienen sentido.
  2. Aceptar que el juego es una base local y no invertir más en el mapa 1024. El radar queda como flavor o se recorta.
- Decidir antes de agregar bosques/cristales, porque esos recursos empujan al jugador a explorar.

---

## Preguntas abiertas (respondidas 2026-10-29)

1. ¿La chatarra es un recurso nuevo o una forma de componentes?
la chatarra es un nuevo recurso que se puede convertir en mineral, se usará para algunas investigaciones tambien.
2. ¿El reciclador reemplaza a la mina/fabricador o los complementa?
el reciclador los complementa, es barato y convierte chatarra en mineral
3. ¿El inicio con módulos destruidos es fijo o procedural?
el inicio con chatarra al rededor es procedural
4. ¿Los bosques y cristales son base o DLC?
los bosques y cristales son base, pero su implementacion nos sirve para analizar como hacer parametrizable la creacion de recursos para un futuro dlc
5. ¿El mapa sigue siendo 1024×1024 o se achica?
le mapa sigue siendo como esta
6. ¿La comida debe ser un problema recurrente o resolverse una vez?
la comida puede ser recurrente, la comida se gastará luego en fabricar biodisel, como consumible en la fabricacion de trampas (tener en cuenta que las construcciones pueden requerir mas de un material)
7. ¿El agua debe escasear para que el condensador tenga rol?
el agua del mapa puede llegar a desaparecer o depender de rng, condensador es fuente alternativa
8. ¿La energía necesita batería o alcanza con storage/caps?
la energia necesita bateria, el cap inical asume ser la bateria del modulo habitacional
9. ¿El objetivo del juego después de estabilizar O2 es expandirse, investigar o sobrevivir a eventos?
luego de estabilizar la superivencia, expancion, investigacion, eventos aleatorios, nuevos modulos, nuevos recursos, pero no pensamos en eso hasta tener bien afinado lo actual


## Reanálisis contra catálogo, diseño y plan (2026-10-29)

Las respuestas cierran la dirección, pero no el orden. El choque principal es que `plan.md` pide **un slice a la vez** y prohíbe recursos nuevos hasta completar la matriz de 2 fuentes/2 usos, mientras que las respuestas 1, 4 y 6 agregan chatarra, bosques, cristales, biodiésel y construcciones multi-material. La respuesta 9 dice que eso va después de afinar lo actual. Interpretación de trabajo (a confirmar): **diseñar ahora, implementar después del playtest**, salvo que se decida lo contrario.

### Decisiones que quedan firmes

- **Chatarra**: recurso intermedio, no vital. Aparece en ruinas procedurales y por demolición; se convierte en mineral y también se gasta en investigaciones.
- **Reciclador**: barato; complementa mina/fabricador, no los reemplaza.
- **Bosques y cristales**: contenido base, pero su implementación debe servir para probar creación parametrizable de recursos para un DLC. El mapa sigue en 1024×1024.
- **Comida**: problema recurrente; se gasta en fabricar biodiésel y en la fabricación de trampas; las construcciones pueden pedir más de un material.
- **Agua**: los depósitos pueden agotarse o depender de RNG; el condensador es la fuente alternativa.
- **Energía**: necesita batería; el cap inicial representa la batería del hábitat.
- **Post-supervivencia**: expansión, investigación, eventos, módulos y recursos nuevos, pero recién cuando lo actual esté afinado.

### Choques y vacíos en los docs

1. **Regla de recursos vs respuestas.** `plan.md` dice que no se agrega un recurso hasta que los seis actuales tengan dos fuentes y dos usos. Hoy energía, comida, mineral y componentes tienen una sola fuente. Chatarra, bosques, cristales y biodiésel son recursos nuevos, y la respuesta 9 los pospone. Hay que decidir si la regla se mantiene (lo nuevo queda como diseño/backlog), se reemplaza por una taxonomía (vital / industrial / intermedio) o se completa la matriz primero.
2. **Catálogo incompleto.** `catalogo.md` es fuente única y no tiene chatarra, reciclador, bosques, cristales, biodiésel, trampa de peces ni los cambios de batería. "Si no está aquí, no existe": hay que decidir si se agregan como `hecho`, `planeado` o `backlog`, con IDs y categorías.
3. **Salida del reciclador.** La idea original decía "componentes nuevos"; las respuestas 1 y 2 dicen "mineral". Si es mineral, el reciclador alimenta al fabricador; si es componentes, compite con él. Definir antes de fijar números.
4. **Demolición.** `catalogo.md` pone la demolición detrás de `reciclaje` (T2, ~50% de retorno); el análisis pide demoler desde el inicio con reembolso parcial. Si la demolición temprana produce chatarra, cambia la fuente inicial y la economía. Decidir si `reciclaje` mejora el retorno o sigue siendo el desbloqueo.
5. **Batería vs almacén.** El código actual da +40 a **todos** los caps con `storage`, incluida energía; `battery` está en backlog y `bateria` es T2 detrás de `solar_ii`. La respuesta 8 dice que la energía necesita batería, pero no define qué aporta frente al almacén ni si `storage` deja de dar cap de energía. Además, el sol solo produce entre las 6 y las 18 h: la batería puede almacenar el excedente diurno, pero `plan.md` dice que "la producción no depende de la luz" (aclarar que se refiere a la lámpara, no al ciclo solar).
6. **Trampas.** `catalogo.md` tiene "Trampa" en Defensa y dice que Defensa no aparece hasta que exista combate. La respuesta 6 habla de trampas que usan comida en su fabricación; lo más probable es que sea la trampa de peces. Separar IDs (`fish_trap` vs `defense_trap`) y decidir si es consumible/reconstruible.
7. **Construcciones y tecnologías multi-material.** Hoy `ModuleDef.cost` y `TechDef.cost` son un `float` de componentes; la UI, el reembolso y el save asumen un solo material. La respuesta 6 pide construcciones con más de un material y la 1 usa chatarra en investigaciones. Esto es un cambio de esquema (save v4), no solo de números.
8. **Barra superior y panel.** `diseno-juego.md` ya dice barra con 4 vitales; el código dibuja 4 vitales + mineral/componentes, y este doc decía "seis". La idea nueva es dejar solo los vitales y mover el resto a "modo recursos". El panel del módulo dice "flujos" en `diseno-juego.md`, pero la idea nueva es mostrar solo producción. Hay que corregir la info y decidir el diseño, no asumir que el doc y el código coinciden.
9. **Ruinas procedurales vs seed/save.** El mundo usa `WORLD_SEED` fijo y los depósitos iniciales están en posiciones fijas. La chatarra procedural necesita un RNG determinista y guardar el estado restante (ruinas consumidas) para que cargar no la regenere. Decidir si el radar/visión la revela y si puede bloquear construcción.
10. **Agua RNG y arranque.** Si el agua puede desaparecer y depender de RNG, un seed malo puede dejar al jugador sin agua ni energía para el condensador. Decidir si hay un depósito inicial garantizado, un mínimo de energía y un aviso antes de quedarse sin fuente.
11. **Comida recurrente vs balance actual.** Hoy el invernadero produce 10/día y el hábitat consume 8/día: sobran 2/día. Si la comida también se gasta en biodiésel, trampas y construcción, ese margen no alcanza. Definir los sinks y si hacen falta trampa de peces, invernadero Mk II u otra fuente.
12. **Pestañas y categorías vacías.** `catalogo.md` pide "sin pestañas vacías" y Defensa no aparece hasta el combate; la idea de pestañas debe ocultar o deshabilitar categorías vacías. Los módulos bloqueados ya se muestran en gris en el código; falta decidir si las pestañas reemplazan los encabezados actuales.

### Preguntas nuevas

**Orden y alcance**

1. ¿La regla de 2 fuentes/2 usos se mantiene para los seis recursos actuales y se relaja para intermedios como la chatarra, o se reemplaza por una taxonomía?
2. ¿Qué se implementa antes del playtest: solo UI/balance actual, o también chatarra/reciclador? La respuesta 9 sugiere lo primero.
3. ¿Los recursos nuevos se agregan al catálogo como `backlog` ahora, o se diseñan acá y se pasan al catálogo recién después del playtest?
4. ¿Cuál es el próximo slice concreto y su criterio de aceptación?

**Chatarra y reciclador**

5. ¿La chatarra entra a la red (stock con cap, save, panel) o es un inventario aparte? ¿Se muestra en "modo recursos"?
6. ¿Cómo se recoge: acción sobre ruinas, módulo recolector, cable, o el reciclador la absorbe?
7. ¿El reciclador produce solo mineral o también componentes? ¿Qué pasa con el fabricador en cada caso?
8. ¿Ratio chatarra→mineral, tiempo, energía y coste del reciclador? ¿Requiere tecnología o está desde el inicio? ¿Por qué no vuelve obsoleta a la mina?
9. ¿Demoler módulos propios da chatarra, mineral o ambos? ¿Se puede reciclar en loop? ¿Qué evita el abuso?
10. ¿La chatarra para investigación se gasta al iniciar la tecnología o durante? ¿Qué tecnologías y cuánto? ¿Compite con convertirla en mineral?
11. ¿Las ruinas procedurales están garantizadas, usan seed y se guardan? ¿Pueden bloquear construcción? ¿Las revela el radar o la visión inicial?

**Bosques, cristales y parametrización**

12. ¿Qué problema resuelve cada recurso y qué dos usos tiene? Sin eso, chocan con la regla de la matriz.
13. ¿Los bosques son renovables/replantables? ¿Los cristales son finitos y requieren radar? ¿Qué módulo y placement usa cada uno?
14. ¿Ambos son base desde el inicio o se desbloquean? ¿En qué categoría/pestaña?
15. ¿Se crea `resource_defs` antes de agregarlos? ¿Qué campos (ID, nombre, icono, vital, cap, color, fuentes/usos) y cómo afecta save/UI?
16. ¿El mapa 1024 mantiene recursos iniciales a 2-5 tiles o se alejan para que el radar tenga sentido? Las respuestas 5 y 7 apuntan a que el radar puede volverse necesario.

**Comida, biodiésel y construcción**

17. ¿Qué consume biodiésel y qué módulo lo produce? ¿Es recurso nuevo, combustible o estado? ¿Compite con comer?
18. ¿"Trampa" es trampa de peces (comida), trampa de defensa (combate) o ambas? ¿Es consumible/reconstruible? ¿Qué consume al fabricarse y qué produce o consume al usarse?
19. ¿Qué construcciones requieren más de un material? ¿Se paga al iniciar? ¿Cómo se muestra, cancela y reembolsa? ¿La comida usada puede matar de inanición?
20. ¿Las tecnologías también costarán múltiples materiales (chatarra, mineral, comida)? Hoy `TechDef.cost` es solo componentes.

**Agua y energía**

21. ¿El agua RNG reemplaza los depósitos iniciales fijos o se suma? ¿Hay un depósito inicial garantizado para no perder por seed?
22. ¿"El agua puede desaparecer" es agotamiento, evento o estación? ¿Se regenera? ¿El radar la encuentra?
23. Si el agua depende del condensador, quedarse sin energía puede matar por sed: ¿se acepta o hace falta un fallback?
24. ¿La batería es un módulo, una capacidad del hábitat o una mecánica de carga? ¿Qué la diferencia del almacén, que hoy da +40 a todos los caps? ¿`storage` deja de dar energía?
25. ¿La batería se desbloquea desde el inicio o sigue detrás de `bateria`/`solar_ii`? Si es necesaria para sobrevivir, no puede ser backlog T2.
26. ¿La batería almacena el excedente diurno (sol 6-18) para la noche o solo amplía el cap? ¿Cambia el balance de solar?

**UI y documentación**

27. ¿La barra superior queda con 4 vitales y mineral/componentes pasan a "modo recursos"? ¿Dónde se ven chatarra, bosque, cristal y biodiésel?
28. ¿"Modo recursos" es un modo nuevo, una pantalla o un panel? ¿Pausa? ¿Muestra nombres, iconos, caps y fuentes/usos?
29. ¿Menú de construcción con pestañas: qué pasa con categorías vacías (Defensa) y con módulos bloqueados? ¿Se ocultan o se muestran en gris?
30. ¿Panel del módulo solo producción: qué se muestra en módulos que solo consumen (laboratorio, radar, lámpara) y dónde queda el consumo de agua/energía/mineral?
31. ¿Ayuda contextual/menú de ayuda: qué contiene y cuándo se abre?
32. ¿Los docs canónicos se actualizan con estas decisiones ahora o después del playtest? (No desde este doc.)

### Impacto técnico (para dimensionar, no implementado)

| Decisión | Impacto |
|----------|---------|
| Chatarra como recurso | `ResourcePool`/`Stockpile`, caps, save, UI y matriz de recursos |
| Multi-material | `ModuleDef.cost` y `TechDef.cost` de `float` a mapa; construcción, reembolso, UI y save v4 |
| Ruinas procedurales | Worldgen con seed, estado restante en save, visión/radar |
| Batería | `module_defs`, `network_caps`, tecnología y diferenciación con `storage` |
| Agua RNG | Worldgen, garantía de inicio, radar y dependencia energía/condensador |
| Pestañas/modo recursos | UI, input, pausa e i18n |

### Próximo orden sugerido (revisado)

1. Playtest de 4B/4C y cerrar la UI ya identificada (barra con 4 vitales, nombres/iconos, pestañas, indicador de pausa, estado del módulo). No agregar recursos todavía.
2. Decidir la taxonomía de recursos y si la regla 2 fuentes/2 usos se mantiene. Recién entonces actualizar `plan.md` y `catalogo.md`.
3. Cerrar números del balance actual (margen inicial, Cmp iniciales, O2 residual y dependencia de agua del invernadero, condensador/radar).
4. Diseñar chatarra/reciclador y demolición; validar contra mina/fabricador y definir recolección, ratio y save.
5. Resolver batería vs almacén y el modelo de energía; después agua RNG y radar.
6. Recién después: bosques, cristales, biodiésel, trampa de peces, construcciones multi-material y recursos parametrizables.
7. Al final, expansión, eventos y contenido nuevo (respuesta 9).
