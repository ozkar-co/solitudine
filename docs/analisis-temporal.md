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
- Tests nuevos: días netos, extractor agotado sin consumo, menú de pausa/créditos, scroll y easter egg.
- **Menú de pausa** con Continuar / Créditos y modal de créditos con scroll (equipo, apoyo, agradecimientos y licencias).

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
- **Menú de pausa con créditos** (implementado): Continuar y Créditos; Créditos abre un modal con scroll que incluye equipo (ozkr, DeepSeek, Retro Diffusion, JuanDi, Neozound, Laura), apoyo (Neo & Cleo), agradecimientos (comunidad open source/open hardware, Python, pygame-ce, PortMaster/R36S) y licencias (Python PSF, pygame-ce LGPL, VT323 SIL OFL 1.1).
- **Hacer visible el modo.** No hay badge persistente de MODO, no se marca el tile seleccionado y el cursor siempre es igual. A cambia de significado según el modo.
- **Estado real del módulo** (implementado en parte): falta que la UI explique mejor el motivo y las acciones disponibles.
- **Iconos sin leyenda.** No hay forma de saber qué representa cada icono. Opciones: menú de ayuda; que el “modo recursos” muestre la lista de recursos con icono y nombre; nombres también en fichas y paneles.
- **Barra superior solo con recursos vitales.** Mostrar solo O2, agua, comida y energía; mineral y componentes pasan a un modo/panel secundario. La barra no puede crecer sin límite.
- **Menú de construcción con pestañas.** Las categorías deben ser pestañas; los módulos no disponibles se muestran en gris con el motivo, no se ocultan.
- **Panel del módulo: producción/consumo relevante.** Mostrar la producción en módulos productores y el consumo en los que solo consumen; los mixtos muestran ambas cosas. Nada de flujos nominales que no importan.
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


## Primera relectura (2026-10-29) — superada por la segunda

> Esta pasada se hizo antes de las respuestas a las 32 preguntas. La “Segunda relectura”, al final del documento, la reemplaza.

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
2 fuentes/ 2 usos no es una regla estricta, es una sugerencia para evaluar y evitar crear recursos de un solo uso o de una sola fuente, a menos que valga la pena.
2. ¿Qué se implementa antes del playtest: solo UI/balance actual, o también chatarra/reciclador? La respuesta 9 sugiere lo primero.
primero solo UI/balance que son los cambios que estan rompiento, el resto se debe acomodar en el plan (reformandolo por completo si hace falta, por eso este analisis es temporal e importante dejarlo claro todo antes de reescribir el plan)
3. ¿Los recursos nuevos se agregan al catálogo como `backlog` ahora, o se diseñan acá y se pasan al catálogo recién después del playtest?
todo lo que se diseñe pasa al catalogo segun su estado, si se implementa con su definicion, si no backlog.
4. ¿Cuál es el próximo slice concreto y su criterio de aceptación?
inmediato arreglar la UI el balance. lo siguiente dependerá del plan.

**Chatarra y reciclador**

5. ¿La chatarra entra a la red (stock con cap, save, panel) o es un inventario aparte? ¿Se muestra en "modo recursos"?
entra a la red y se muestra entre los recursos.
6. ¿Cómo se recoge: acción sobre ruinas, módulo recolector, cable, o el reciclador la absorbe?
es una accion sobre las ruinas, se puede recoger desde el dia 0 pero quizas no se pueda usar aun, el monto de chatarra que produce una ruina es variable y esta almacenado en ella (se define en su creacion) al destruir un modulo pasa a ser ruinas y la chatarra es proporcional al costo que tuvo.
7. ¿El reciclador produce solo mineral o también componentes? ¿Qué pasa con el fabricador en cada caso?
el reciclador solo produce mineral, pero tiene chances muy bajos de producir trazas de otros materiales, en su info lleva el registro de cuanta chatarra ha procesado y que ha producido.
8. ¿Ratio chatarra→mineral, tiempo, energía y coste del reciclador? ¿Requiere tecnología o está desde el inicio? ¿Por qué no vuelve obsoleta a la mina?
requiere una tecnologia, consume poca energia y es barato, no se exactamente cuanto debemos comparar con otros modulos, pienso quizas 2 o 3 de componentes, se construye en medio dia y gasta 1 de energia y 0.5 de agua. para investigarlo se requieren 5 de chatarra, 2 componentes y 1 mineral.
no vuelve obsoleta la mina porque la chatarra en el mundo es un recurso limitado, rng y menos abundante que las minas, es solo el extra que cierra el ciclo de cuando destruyo algo que construí, resuelve el tener mas de una fuente de minerales y añade el primer componente "gacha" al juego.
9. ¿Demoler módulos propios da chatarra, mineral o ambos? ¿Se puede reciclar en loop? ¿Qué evita el abuso?
demoler modulos propios produce chatarra pero siempre menos que el mineral equivalente que se usó para construirlos, produce entre un 0.6 y un 0.9 (equivalente en chatarra) a los minerales usados para crear la cantidad de componenetes que se usaron para construirlo. cancelar una construccion produce un porcentaje de chatarra equivalente al progreso que llevaba con un cap de 0.9
10. ¿La chatarra para investigación se gasta al iniciar la tecnología o durante? ¿Qué tecnologías y cuánto? ¿Compite con convertirla en mineral?
los materiales requeridos para iniciar una investigacion se gastan al iniciar la investigación inmediatamente, asi no compite.
11. ¿Las ruinas procedurales están garantizadas, usan seed y se guardan? ¿Pueden bloquear construcción? ¿Las revela el radar o la visión inicial?
si hay unas garantizadas pero pocas el resto se generan como los lagos o depositos de minerales. bloquean la construccion.

**Bosques, cristales y parametrización**

12. ¿Qué problema resuelve cada recurso y qué dos usos tiene? Sin eso, chocan con la regla de la matriz.
estos son ideas que aun no se terminan de desarrollar pero apuntan a ser requisitos de inverstigacion, materiales de construccion de modulos nuevos que aun no nos hemos inventado y consumibles de modulos que aun no nos hemos inventado.
13. ¿Los bosques son renovables/replantables? ¿Los cristales son finitos y requieren radar? ¿Qué módulo y placement usa cada uno?
los bosques son renovables, dejan los brotes en el suelo pero toman varios meses en volver a crecer. los cristales son finitos y solo aparecen bajo tierra.
14. ¿Ambos son base desde el inicio o se desbloquean? ¿En qué categoría/pestaña?
ambos estan desde el principio asi el jugador se pregunta ¿que será esto, como lo obtengo? podemos incluso añadirlos de una vez aunque no sean obtenibles.
15. ¿Se crea `resource_defs` antes de agregarlos? ¿Qué campos (ID, nombre, icono, vital, cap, color, fuentes/usos) y cómo afecta save/UI?
debemos analizar como estan definidos los otros recursos para poder crear un estandar.
16. ¿El mapa 1024 mantiene recursos iniciales a 2-5 tiles o se alejan para que el radar tenga sentido? Las respuestas 5 y 7 apuntan a que el radar puede volverse necesario.
los recursos iniciales es para evitar partidas donde sea imposible sobrevivir al pirincipio y tener recursos para poder explorar, una vez se agotan toca explorar y para eso el radar es fundamental.

**Comida, biodiésel y construcción**

17. ¿Qué consume biodiésel y qué módulo lo produce? ¿Es recurso nuevo, combustible o estado? ¿Compite con comer?
biodisel seria otro recurso mas, similar a madera y cristales. solo que este (al igual que los componentes) no se extrae si no que se produce, todos los recursos que se gastan por mas de un modulo o supervivencia (modulo habitacional) compiten, para eso se implementará la posibilidad de apagarlos, para que el jugador controle, si se esta quedando sin un recurso cuales son los que deben seguir funcionando.
18. ¿"Trampa" es trampa de peces (comida), trampa de defensa (combate) o ambas? ¿Es consumible/reconstruible? ¿Qué consume al fabricarse y qué produce o consume al usarse?
tenemos dos tipos de trampas la de peces que será inical y la alternativa a conseguir comida del invernadero. es barata (1 o 2 componentes) requiere ponerse sobre agua y estar conectada a la red (aunque no consuma energia) produce de forma aleatoria 1 o 2 de comida y solo durante la noche, no es una fuente primaria (a menos que se tengan muchas) y si el agua se seca deja de producir. la trampa de defensa es otra para la fase donde se implementen las alimañas, aun no se ha definido, será el complemento a las torretas quizas haga de varios tipos (explosivas, cebo, etc...) pero se define bien cuando lleguemos a ese punto.
19. ¿Qué construcciones requieren más de un material? ¿Se paga al iniciar? ¿Cómo se muestra, cancela y reembolsa? ¿La comida usada puede matar de inanición?
todo costo (al igual que componentes) se paga al iniciar, componentes es el base o principal de la mayoria de recursos, el menu de construccion debe mostrar el costo de cada construccion, por eso se planteo reformular y que las categorias sean pestañas, para dar mas espacio a tener mas detalles de cada construccion. depende mucho de la logica saber que extras gastar, por ejemplo tiene sentido usar una pequeña cantidad de minerales en bruto para construir el invernadero, o usar chatarra para construir el fabricador o el laboratorio, muchos van a seguir costando solo componentes, pero el motor del juego debe permitir tener mas de un costo.
20. ¿Las tecnologías también costarán múltiples materiales (chatarra, mineral, comida)? Hoy `TechDef.cost` es solo componentes.
exacto, por ejemplo cristales para algunas tecnologias avanzadas o recursos relacionados con la naturaleza de la investigacion.

**Agua y energía**

21. ¿El agua RNG reemplaza los depósitos iniciales fijos o se suma? ¿Hay un depósito inicial garantizado para no perder por seed?
se suma y hay uno garantizado para no perder por seed.
22. ¿"El agua puede desaparecer" es agotamiento, evento o estación? ¿Se regenera? ¿El radar la encuentra?
el agua desaparece, por ahora se agota por el extractor (creo que ya esta implementado) no se regenera, el radar encuentra todo, es la unica forma de explorar por ahora. podrian haber eventos que agoren el agua pero no pensar en eso.
23. Si el agua depende del condensador, quedarse sin energía puede matar por sed: ¿se acepta o hace falta un fallback?
esta es una de las formas en que quedarse sin energia puede matar, y esta bien asi.
24. ¿La batería es un módulo, una capacidad del hábitat o una mecánica de carga? ¿Qué la diferencia del almacén, que hoy da +40 a todos los caps? ¿`storage` deja de dar energía?
la bateria es el equivalente al almacen para la energia, el almacen deja de aumentar el cap de energia, a medida que creemos modulos especializados (por ejemplo tanques y asi) podriamos ir quitando capacidades al almacen, por ahora solo las baterias, pero se puede tener en cuenta para modificar el almacen en el futuro.
25. ¿La batería se desbloquea desde el inicio o sigue detrás de `bateria`/`solar_ii`? Si es necesaria para sobrevivir, no puede ser backlog T2.
la bateria sigue detras de una investigacion, el modulo habitacional tiene una capacidad de carga de entrada y para todo lo demas antes de la investigacion queda producir lo que se consume 
26. ¿La batería almacena el excedente diurno (sol 6-18) para la noche o solo amplía el cap? ¿Cambia el balance de solar?
la bateria solo aumenta el cap, el almacenamiento del excedente esta contemplado en la funcionalidad actual sin consideraciones especiales.

**UI y documentación**

27. ¿La barra superior queda con 4 vitales y mineral/componentes pasan a "modo recursos"? ¿Dónde se ven chatarra, bosque, cristal y biodiésel?
en modo recursos aparecen todos los recursos. si en la barra superior caben los nombres, los vitales se omiten del modo recursos, si en la barra superior quedan solo los simbolos, modo recursos los incluye para que el usuario pueda ver los nombres de esos recursos en algun lugar (y no depender de ayudas)
28. ¿"Modo recursos" es un modo nuevo, una pantalla o un panel? ¿Pausa? ¿Muestra nombres, iconos, caps y fuentes/usos?
es un modo que ya existe (el que permite ver los subterraneos, el de la tecla X (c en teclado))
29. ¿Menú de construcción con pestañas: qué pasa con categorías vacías (Defensa) y con módulos bloqueados? ¿Se ocultan o se muestran en gris?
las categorias vacias se ocultan, si tienen cosas que no estan disponibles esas si se muestran en gris.
30. ¿Panel del módulo solo producción: qué se muestra en módulos que solo consumen (laboratorio, radar, lámpara) y dónde queda el consumo de agua/energía/mineral?
en los que solo consumen se muestran datos sobre su consumo. y para todos una breve descripcion de lo que hace el modulo y cuando fue construido (asi incluso los mas basicos tendran algo que mostrar)
31. ¿Ayuda contextual/menú de ayuda: qué contiene y cuándo se abre?
en lo posible evitaremos tener ayuda y que el juego sea autoexplicativo o que tenga yo como jugador algun modo de descubrir para que sirve cada cosa aunque sea experimentado.
32. ¿Los docs canónicos se actualizan con estas decisiones ahora o después del playtest? (No desde este doc.)
cuando yo lo diga explicitamente.

### Impacto técnico (para dimensionar, no implementado)

| Decisión | Impacto |
|----------|---------|
| Chatarra como recurso | `ResourcePool`/`Stockpile`, caps, save, UI y matriz de recursos |
| Multi-material | `ModuleDef.cost` y `TechDef.cost` de `float` a mapa; construcción, reembolso, UI y save v4 |
| Ruinas procedurales | Worldgen con seed, estado restante en save, visión/radar |
| Batería | `module_defs`, `network_caps`, tecnología y diferenciación con `storage` |
| Agua RNG | Worldgen, garantía de inicio, radar y dependencia energía/condensador |
| Pestañas/modo recursos | UI, input, pausa e i18n |

### Próximo orden sugerido (primera pasada, superado)

1. Playtest de 4B/4C y cerrar la UI ya identificada (barra con 4 vitales, nombres/iconos, pestañas, indicador de pausa, estado del módulo). No agregar recursos todavía.
2. Decidir la taxonomía de recursos y si la regla 2 fuentes/2 usos se mantiene. Recién entonces actualizar `plan.md` y `catalogo.md`.
3. Cerrar números del balance actual (margen inicial, Cmp iniciales, O2 residual y dependencia de agua del invernadero, condensador/radar).
4. Diseñar chatarra/reciclador y demolición; validar contra mina/fabricador y definir recolección, ratio y save.
5. Resolver batería vs almacén y el modelo de energía; después agua RNG y radar.
6. Recién después: bosques, cristales, biodiésel, trampa de peces, construcciones multi-material y recursos parametrizables.
7. Al final, expansión, eventos y contenido nuevo (respuesta 9).

---

## Segunda relectura (2026-10-29)

Las 32 respuestas y las 23 respuestas inline permiten cerrar la estructura y reescribir el plan. Lo que sigue registra el estado que se fue cerrando; el “Cierre del análisis”, al final, resume el resultado.

Para reescribir el plan no hacía falta cerrar los 23 puntos: alcanzaba con seis decisiones estructurales: (1) estándar de recursos/costes; (2) tecnología y economía de chatarra/reciclador/demolición; (3) conexión y rol de la trampa de peces; (4) batería/almacén y carga; (5) agua/radar; (6) arquitectura de información de la UI. Los números finos quedan para el plan/playtest.

### Estado de claridad

| Tema | Decisión | Estado |
|------|----------|--------|
| Orden inmediato | UI/balance primero; el plan se reescribe después de cerrar este análisis; los docs canónicos se actualizan cuando el usuario lo diga | Claro |
| Regla de recursos | 2 fuentes/2 usos es una heurística, no una regla estricta; se aceptan excepciones si valen la pena | Claro |
| Catálogo | Todo lo diseñado entra según su estado: implementado con definición, si no `backlog` | Claro; falta sección de recursos |
| Chatarra | Recurso de red, visible en modo recursos; se recoge de ruinas desde el día 0; monto variable por ruina | Casi; faltan cap y números |
| Ruinas | Pocas garantizadas + procedurales; bloquean construcción; el radar revela todo | Casi; faltan placement y guardado |
| Reciclador | Requiere tecnología; barato (2-3 Cmp propuesto, 0,5 día, 1 E/d y 0,5 agua/d asumidos); chatarra→mineral; trazas raras; registra procesado/producido; investigación 5 chatarra + 2 Cmp + 1 mineral | Casi; faltan tecnología, trazas y ratio |
| Demolición/cancelación | Demoler devuelve 0,6-0,9 del equivalente mineral; cancelar devuelve el progreso con cap 0,9 | Falta fórmula y ejemplo |
| Comida | Recurrente; se gasta en biodiésel y en fabricar trampas; costes multi-material | Claro; falta biodiésel |
| Trampa de peces | 1-2 Cmp, sobre agua, conectada a la red, 1-2 comida/noche, se detiene si el agua se agota; la de defensa es posterior | Casi; falta conexión en agua y números |
| Agua | Garantizada + RNG, finita, sin regeneración; el radar es la única exploración; quedarse sin energía puede matar por sed | Claro; faltan tamaños y radar |
| Energía | Batería = cap de energía; el almacén deja de dar energía; la batería solo aumenta cap; requiere investigación; el hábitat tiene el cap inicial | Casi; falta “carga de entrada” y tecnología |
| Bosques/cristales | Base; visibles desde el inicio aunque no sean obtenibles; bosques renovables, cristales subterráneos finitos; usos sin diseñar | Falta diseño |
| Biodiésel | Recurso producido; compite con otros consumos; se controla apagando módulos | Falta productor y consumidor |
| Multi-material | Todo se paga al inicio; componentes es la base; las pestañas dan espacio para mostrar costes | Falta tabla y política de reembolso |
| UI | Barra con 4 vitales; modo recursos (X/C) con nombres; pestañas; panel de producción/consumo + descripción/fecha; menú de pausa con Continuar/Créditos; evitar ayuda | Casi; faltan layout, Defensa y panel mixto |
| Docs | Se actualizan solo cuando el usuario lo pida explícitamente | Claro |

### Huecos que pueden romper la implementación

> Detectados antes de las respuestas inline. El “Cierre del análisis”, al final, los resuelve y deja solo tuning pendiente.

1. **Fórmula de chatarra.** La respuesta 9 es difícil de verificar sin un ejemplo. Con la economía actual, 6 Cmp equivalen a 9 mineral (fabricador: 6 mineral → 4 Cmp). Demoler devuelve 0,6-0,9 de ese equivalente: 5,4-8,1 chatarra. Si el reciclador convierte 1:1, se recuperan 5,4-8,1 mineral; si el ratio es menor, menos. Hay que fijar el ratio, el rango y un ejemplo cerrado, o el loop económico queda indefinido.
2. **Tecnología del reciclador y demolición.** El catálogo tiene `reciclaje` como T2 detrás de `fabricacion_ii` y le asigna desbloquear la demolición con ~50%. Las respuestas dicen que la demolición existe desde el inicio (o al menos que destruir un módulo produce ruina/chatarra) y que el reciclador requiere una tecnología. Hay que decidir si `reciclaje` es la tecnología del reciclador, qué desbloquea exactamente y en qué tier queda. Si es T2, la chatarra se acumula desde el día 0 sin poder procesarse durante mucho tiempo.
3. **Trazas del reciclador.** “Trazas muy bajas de otros materiales” no dice cuáles, con qué probabilidad ni en qué cantidad. Es el primer componente gacha: hay que definir tabla, RNG determinista o no, protección contra save-scum y cómo se muestra en la info del módulo.
4. **Chatarra en la red.** Entra a la red y se muestra entre los recursos, pero falta cap, si el almacén le da +40, si usa buffer, qué pasa al llenarse y cómo entra en el save. Si se llena, la recogida de ruinas se desperdicia sin aviso.
5. **Ruinas.** No está claro si ocupan uno o varios tiles, si bloquean cables además de construcción, cómo se guarda el monto variable, si demoler crea una ruina que hay que recoger o da chatarra directa, y si las ruinas garantizadas pueden caer sobre depósitos iniciales o el camino del cable.
6. **Trampa de peces y cable en agua.** El cable actual solo se coloca en suelo. La trampa va “sobre agua” y debe estar conectada: hay que definir si se conecta desde la orilla, si el cable puede cruzar agua o si es inalámbrica. Además, ¿ocupa el tile de agua y bloquea al extractor? ¿Qué pasa con la trampa cuando el agua se agota?
7. **Costes multi-material y reembolsos.** Falta la tabla de qué módulos usan mineral/chatarra/comida además de componentes, cómo se muestra la falta de cada material, qué se devuelve al cancelar/demoler (¿chatarra de todo o solo de componentes?), cómo se guarda una obra en curso y si la comida usada en construcción puede matar de inanición.
8. **Energía.** “El módulo habitacional tiene una capacidad de carga de entrada” puede significar un cap o un límite de energía por día; el código actual no tiene límite de carga. También falta el tier/prerequisito de la batería y confirmar que el almacén sigue dando +40 a todos los recursos menos energía, incluidos chatarra/biodiésel/madera/cristal.
9. **Biodiésel.** No hay productor ni consumidor definido. ¿Qué módulo lo produce, con qué insumos, en qué ratio y qué lo consume? ¿Es un stock normal o un tanque aparte?
10. **Bosques y cristales.** Los usos son “módulos que aún no inventamos”; no se pueden agregar al catálogo con números. Además, “varios meses” de regrowth necesita una escala concreta (días de juego), y hay que decidir si se agregan como scenery inerte ahora o solo cuando exista al menos un uso.
11. **UI.** Quedan abiertos: nombres vs símbolos en la barra, comportamiento y pausa del modo recursos, si Defensa se oculta o se muestra en gris, qué muestra el panel de un módulo mixto (invernadero) y si “evitar ayuda” elimina también los hints contextuales.
12. **Reescritura del plan.** El usuario dijo que el plan puede reescribirse completo. Falta decidir la estructura objetivo y si se actualizan plan/catálogo/diseño en ese orden o en paralelo (siempre cuando lo pida explícitamente).

### Preguntas nuevas

**Números y fórmulas**

1. ¿Confirmas este ejemplo? 6 Cmp = 9 mineral; demoler devuelve 5,4-8,1 chatarra; con ratio 1:1 se recuperan 5,4-8,1 mineral. ¿Qué ratio chatarra→mineral y qué velocidad de procesamiento (chatarra/día) usamos?
me parece perfecto, el ratio de chatarra que sea 0.9 solo para justificar el "proceso" y las trazas ocacionales. el unico que se destruye y devuelve los componentes integros es el cable (caso especial)
2. ¿La cancelación de obra devuelve chatarra de todos los materiales o solo del equivalente a componentes? ¿Cómo se calcula con costes multi-material?
solo el equivalente a componentes, por eso es un riesgo, los extra se pierden.
3. ¿El reciclador usa la tecnología `reciclaje` del catálogo o una nueva? ¿Qué tier/prerequisito tiene? ¿`reciclaje` sigue desbloqueando demolición o la demolición ya está desde el día 0?
la demolicion esta desde el dia 0, con confirmacion, por ahora solo tenemos un tier de tecnologias, a medida que pongamos mas vamos dandole forma al arbol, lo importante era saber que el arbol va a existir para que desde el principio el motor del juego lo soporte
4. ¿Qué trazas produce el reciclador (materiales, probabilidades, cantidades)? ¿Se guardan en el save? ¿Se puede save-scum?
se guardan en el save, hagamos que sean aleatorios y como estamos guardando al salir y tendremos auto saves regulares y no se sabe cuando saldran materiales y son pocas cantidades (no es fuente principal y es muy esporadico) no nos importa el save-scum
pues aqui es donde se recuperan esos materiales que se perdieron al destruir los modulos, a veces sacará cristales, a veces sacará madera, a veces sacará mas chatarra, a veces sacará componentes, algunos serán mas probables otros menos probables.
5. ¿La chatarra tiene cap propio? ¿El almacén le da +40? ¿Qué pasa si se llena?
si, la chatarra tiene un cap similar incluso menor al de los demas recursos, y el almacen tambien lo amplifica.
6. ¿Cuántas ruinas garantizadas hay, de qué tamaño y dónde? ¿Pueden bloquear depósitos iniciales o el cable? ¿Se guardan?
las ruinas son de tamaño uno y solo se garantizan 2. se guardan, solo aparecen en zonas abiertas, sin agua ni minerales ni arboles, ni cristal, y bloquean la construccion de todo, incluidos cables.
7. ¿Demoler crea una ruina que hay que recoger o da chatarra directa? ¿La ruina ocupa uno o varios tiles? ¿Bloquea cables o solo construcción? ¿La recogida es instantánea o tarda/consume energía?
demoler crea una ruina que se debe recorrer del tamaño del modulo que habia, por ahora creo que todos son de 1x1 entonces es facil, la recogida es instantanea y no consume nada.

**Comida, trampas y construcción**

8. ¿La trampa de peces se conecta por cable desde la orilla, el cable puede ir sobre agua, o es inalámbrica? ¿Comparte tile con el extractor? ¿Qué pasa cuando el agua se agota?
cable puede ir sobre agua, la trampa debe conectarse, la trampa es un modulo, no comparte tile, cuando el agua se agota deja de producir para siempre, queda ahi inutil, se puede destruir (igual que cualquier modulo) para volverlo ruinas y recuperar la chatarra.
9. ¿Qué módulo produce biodiésel, con qué insumos y qué consume? ¿Es storage normal o tanque?
será un modulo que aun no se ha definido, una especie de planta de procesamiento que requerira investigaciones, a definir en el futuro.
10. ¿Qué costes multi-material tienen los módulos actuales? ¿Se define una tabla antes de implementar? ¿La comida usada en construcción puede matar?
se define antes de implementar. la comida si se gasta en construccion si puede matar, quizas mas adelante se implemente un tiempo de gracia luego de que la comida (al igual que el agua y el oxigeno) llega a cero, pero por ahora la muerte es directa.
11. ¿Qué pasa si dos módulos compiten por agua/comida/mineral? ¿El hábitat tiene prioridad o el jugador apaga módulos? ¿Se muestra el conflicto?
si hay competencia se divide a partes iguales no hay prioridades, cada uno va gastando en la medida en que hay disponibilidad. si hay que decidir si uno u otro, al azar.

**Energía y agua**

12. ¿La “capacidad de carga de entrada” del hábitat es un cap o un límite de energía por día? ¿La batería sigue en T2 tras `solar_ii`? ¿Cuánto cap da y cuánto cuesta?
es un cap, representa el funcionamiento actual, la bateria queda en t2
13. ¿El almacén sigue dando +40 a todos los recursos menos energía, incluidos chatarra/biodiésel/madera/cristal? ¿Los tanques especializados son ahora o futuro?
los tanque especializados son el futuro el almacen da +40 a todo lo que no tenga un reservorio especializado.
14. ¿Cuánto dura el depósito de agua garantizado y cuántos depósitos RNG hay? ¿El radar debe abaratarse para que la exploración sea viable?
el deposito de agua funciona tal cual como esta ya implementado, no hay qye cambiar nada aqui.
15. ¿La desaparición del agua cambia el tile (vuelve a suelo) o solo el depósito? ¿Qué pasa con la trampa de peces y el extractor? vuelve a suelo, extractor y trampa quedan ahi, inutiles, recuerda KISS, mantenerlo simple, tal y como funciona actualmente con el extractor.

**Bosques, cristales y contenido**

16. ¿Los bosques y cristales se agregan como scenery inerte ahora o esperan a tener al menos un uso? ¿Cómo se muestran como “no obtenibles” sin ayuda?
no se añade nada aun se define cuando lleguemos a esa etapa.
17. ¿Cuánto tardan los bosques en regrow (días/meses) y cómo se representa el brote? ¿Bloquea construcción?
los bosques y brotes bloquean la construccion, se define cuando llegue el momento de implementarlos.
18. ¿Los cristales se ven en modo recursos antes de tener el extractor? ¿Qué módulo los extrae y qué placement usa?
esto se define cuando llegue el momento, funcionan similar a los depositos subterraneos de minerales.

**UI y plan**

19. ¿La barra superior muestra nombres o solo iconos? Si muestra nombres, ¿modo recursos omite los vitales? ¿Se pausa el modo recursos?
que muestre o no los nombres depende de probar y ver si caben junto a los iconos. y dependiendo de eso se toma la desicion.
20. ¿La pestaña Defensa se oculta hasta combate o se muestra en gris con torreta/trampa? ¿Qué categoría tiene la trampa de peces?
se oculta hasta que esto este implementado (osea desde el principio ni siquiera se menciona)
21. ¿El panel de un módulo mixto (invernadero) muestra producción y consumo, o solo producción? ¿Dónde queda el consumo?
los modulos mixtos muetras produccion y consumo, si alguno no cabe lo analizamos y decidimos para ese caso puntual.
22. ¿“Evitar ayuda” elimina los hints contextuales actuales o solo el menú de ayuda? ¿Cómo se enseña R1/B/X?
solo el menu de ayuda los hints actuales se mantienen, es no tener trabajo extra.
23. ¿El plan se reescribe completo antes de tocar catálogo/diseño, o se actualizan en paralelo? ¿Qué estructura tendrá?
el plan se reescribe, tal y como te habia dicho cuando yo lo diga explicitamente. tendra varias etapas q modo que cada una sea completamente jugable e introduzca cambios que esten relacionados.

### Impacto técnico actualizado

| Decisión | Impacto |
|----------|---------|
| Chatarra + cap | `Stockpile`/caps, save, modo recursos y almacén |
| Ruinas | Worldgen con seed, datos por tile, save, bloqueo de construcción, radar |
| Reciclador | `module_defs`, tecnología, trazas, estadísticas por módulo, save |
| Demolición/cancelación | Acción, fórmula de retorno, multi-material, save |
| Multi-material | `ModuleDef.cost`/`TechDef.cost` de `float` a mapa; UI de construcción, obra en curso, save v4 |
| Trampa de peces | `module_defs`, placement sobre agua, red/cable, producción nocturna |
| Batería/almacén | `network_caps`, bonus de almacén por recurso, tecnología, balance |
| Agua RNG/radar | Worldgen, depósito garantizado, coste/consumo del radar, avisos |
| Bosques/cristales/biodiésel | Definiciones de recursos, worldgen, módulos, tecnologías, UI |
| Modo recursos/pestañas/panel | UI, input, i18n |

### Nuevo orden sugerido

El orden cambia respecto de la primera pasada: no se implementa chatarra antes de cerrar el estándar de recursos/costes, y no se agregan bosques/cristales/biodiésel hasta tener usos concretos.

1. **Ahora: UI/balance actual y playtest.** Arreglar lo que rompe: barra con 4 vitales (nombres si caben), modo recursos con todos los nombres, pestañas, ocultar categorías vacías, gris para no disponibles, panel con producción/consumo + descripción/fecha, menú de pausa con Continuar/Créditos, indicador de pausa, visibilidad de modo, hints y acentos. Ajustar el balance actual (margen inicial, Cmp, O2 residual, agua del invernadero, condensador/radar) y validarlo en PC y R36S. No agregar contenido nuevo.
2. **Cerrar el análisis estructural.** Resolver las decisiones que bloquean el plan: estándar de recursos/costes; tecnología y fórmula de chatarra/reciclador/demolición; conexión de la trampa de peces; batería/almacén y carga; agua/radar; arquitectura de información de la UI. Los números finos pueden quedar para playtest.
3. **Reescribir el plan (cuando lo pidas).** En la misma pasada, si lo pides, actualizar catálogo (recursos, módulos y tecnologías con estado) y diseño (UI, controles, recursos). No tocar docs canónicos antes.
4. **Fundación técnica.** Estándar de recursos (`resource_defs` o equivalente), costes multi-material, obra en curso, reembolsos y save v4. Es lo que habilita el resto.
5. **Chatarra/reciclador/demolición.** Primer slice de contenido nuevo; probar el loop económico completo.
6. **Trampa de peces + comida.** Segunda fuente de comida, producción nocturna y placement sobre agua.
7. **Batería/almacén + energía.** Separar caps, definir tecnología y semántica de carga; rebalancear.
8. **Agua RNG + radar.** Depósito garantizado + aleatorios, coste/rol del radar, interacción con trampa y extractor, avisos.
9. **Bosques/cristales/biodiésel.** Recién con usos concretos. Si se quieren visibles desde el inicio, agregarlos como scenery inerte en el paso 8 y activar la extracción en este paso.
10. **Expansión, eventos y contenido nuevo.** Último, según la respuesta 9.

---

## Cierre del análisis (2026-10-29)

Con las respuestas a las 23 preguntas, las seis decisiones estructurales quedan cerradas. Los huecos de la segunda relectura se resuelven así:

- **Chatarra/reciclador:** ratio 0,9; demolición 0,6-0,9; el cable devuelve componentes íntegros (caso especial); recogida instantánea y sin coste; cap propio menor que el resto, ampliado por almacén.
- **Tecnología:** demolición desde el día 0 con confirmación; un solo tier actual; el árbol se irá armando y el motor debe soportarlo. El reciclador requiere una tecnología a definir en ese árbol.
- **Trazas:** aleatorias y guardadas; sin protección anti save-scum; recuperan materiales perdidos (cristales, madera, chatarra, componentes), con probabilidades a definir.
- **Ruinas:** 1 tile; 2 garantizadas; guardadas; solo en zonas abiertas sin agua/mineral/árboles/cristales; bloquean todo, incluidos cables.
- **Demoler:** crea una ruina del tamaño del módulo (hoy 1×1); la recogida es instantánea y no consume nada.
- **Trampa de peces:** el cable puede ir sobre agua; es un módulo aparte; al secarse el agua queda inútil para siempre y se puede demoler para recuperar chatarra.
- **Biodiésel:** módulo futuro, sin definir; queda en backlog.
- **Multi-material:** tabla antes de implementar; todo se paga al inicio; la comida usada puede matar; por ahora muerte directa, sin gracia.
- **Competencia:** reparto igualitario, sin prioridades; cada módulo gasta según disponibilidad; empate al azar.
- **Energía:** el cap del hábitat es un cap; la batería queda en T2; el almacén da +40 a todo lo que no tenga reservorio especializado; los tanques especializados son futuro.
- **Agua:** igual que hoy; el tile vuelve a suelo; extractor y trampa quedan inútiles.
- **Bosques/cristales:** no se añaden aún; se definen al llegar a esa etapa; bloquearán construcción.
- **UI:** los nombres en la barra se deciden probando; Defensa se oculta hasta implementarse; los módulos mixtos muestran producción y consumo; los hints se mantienen y solo se quita el menú de ayuda.
- **Plan:** se reescribe por etapas jugables cuando lo pidas.

Queda como tuning, no como arquitectura: tabla exacta de costes multi-material, cap de chatarra, probabilidades de trazas, coste/consumo del radar, números de la trampa, tiempo de regrowth, etc. **El análisis puede cerrarse; el plan puede reescribirse cuando lo pidas.**

### Créditos (implementado)

- Menú de pausa: **Continuar** y **Créditos**. En pausa, LJOY/DPAD elige, A confirma y START o B continúa. En créditos, LJOY/DPAD desplaza y B/START vuelve al menú de pausa.
- El modal tiene scroll por secciones para poder sumar colaboradores sin rediseñarlo:
  - **Equipo:** ozkr (creador/director; diseño, programación y producción), DeepSeek (programación auxiliar), Retro Diffusion (diseño auxiliar de sprites con Genkit, rd-tile / rd-plus), JuanDi (alpha testing y colaboración creativa), Neozound (composición y diseño sonoro) y Laura (secretaria y asistente).
  - **Apoyo:** Neo & Cleo (soporte emocional y musas creativas).
  - **Agradecimientos:** comunidad open source y open hardware; Python; pygame-ce; PortMaster y R36S.
  - **Licencias:** Python (PSF License), pygame-ce (LGPL), VT323 (SIL OFL 1.1).
- El juego permanece pausado con el menú o el modal abiertos.
- Para sumar colaboradores alcanza con agregar entradas en `credits.py` y sus claves en `locales/es.json`; el scroll se recalcula solo.
- **Easter egg sin pistas:** en Créditos, ↑ ↑ ↓ ↓ ← → ← → abre `assets/credits/gatos.png` a pantalla completa; cualquier tecla vuelve a Créditos. La imagen es 640×480, pixelada desde 320×240 y reducida a 32 colores.
