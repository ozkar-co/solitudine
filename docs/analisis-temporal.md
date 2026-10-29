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

- Empezar con **módulos destruidos alrededor** del hábitat.
- Destruir/reciclar módulos existentes produce **chatarra**.
- La chatarra se procesa en un **reciclador** para obtener componentes nuevos.
- El reciclador se desbloquea con una **tecnología nueva después del laboratorio**.
- Preguntas a resolver:
  - ¿La chatarra es un recurso nuevo? Si sí, rompe la regla “no agregar un recurso hasta que los seis actuales tengan dos fuentes y dos usos”. ¿Se puede expresar como componentes con otro nombre/estado?
  - ¿De dónde sale la chatarra inicial? ¿Módulos destruidos fijos, ruinas, lluvia de restos?
  - ¿El reciclador es una fuente infinita? ¿Tiene límite por chatarra o por energía?
  - ¿Reciclar módulos compite con demoler? ¿Qué reembolso da cada uno?
  - ¿Cómo se muestra en el mapa y en el panel?
  - ¿Afecta el guardado? (nuevo stock/recurso → versión de save).

### Nuevos recursos y módulos

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

- Hoy un invernadero resuelve la comida. Una segunda fuente solo tiene sentido si crea una elección.
- Idea: **trampa de peces** barata (4 Cmp, 1 día, +5 comida, sin agua/energía, junto a agua, una por parche). Rol: comida temprana o comida sin agua; el invernadero queda como mejora.
- Si no se quiere una segunda fuente, no agregarla: sería contenido redundante.

### Exploración y mapa

- Los recursos iniciales están a 2-5 tiles; el radar es caro y no hay botín/POI. La exploración no tiene payoff económico.
- Opciones:
  1. Hacer escasos los depósitos locales, reducir el coste/consumo del radar y agregar un aviso “depósito encontrado”. Así el radar y la expansión tienen sentido.
  2. Aceptar que el juego es una base local y no invertir más en el mapa 1024. El radar queda como flavor o se recorta.
- Decidir antes de agregar bosques/cristales, porque esos recursos empujan al jugador a explorar.

---

## Preguntas abiertas

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


## Próximo orden sugerido

1. Validar la info real en playtest (barra superior, panel, debug).
2. Decidir pausa del menú/colocación y visibilidad de modo.
3. Decidir margen inicial, Cmp iniciales y O2 residual del invernadero.
4. Diseñar chatarra/reciclador y su relación con mina/fabricador.
5. Decidir el rol del agua (condensador) y del radar/exploración.
6. Recién después: bosques, cristales, trampa de peces, DLC/escalabilidad.
