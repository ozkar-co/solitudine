# Plan de fase 5 — amenazas, botín y muerte

> **Dependencia:** este bloque va después de la fase 4 (al menos 4A–4C). No abrir combate antes de cerrar el apagado, la consola, el guardado y la matriz de recursos.
> **UI:** el shell, la barra de recursos y la pestaña Carga se construyen en [plan-ui.md](plan-ui.md); aquí solo se conectan los datos.
> Decisiones vigentes: 2026-10-28.

---

## 1. Ideas registradas (segunda tanda)

| ID | Idea | Valor | Esfuerzo | Riesgo | Decisión |
|----|------|-------|----------|--------|----------|
| I6 | Recursos adicionales obtenidos explorando o matando alimañas | Alto | Medio | Medio | Entra con inventario nuevo, no como campos sueltos |
| I7 | Combate tower defense automático | Alto | Alto | Alto | Fase 5, slice corto; no antes de 4A–4C |
| I8 | Radar como única exploración y foco que atrae alimañas; radio de atracción invisible | Alto | Medio-alto | Alto (justicia) | Entra en 5B con avisos diegéticos |
| I9 | Cambiar el conteo/inventario y la barra superior | Alto | Medio | Medio | Prerrequisito de 5B: 5A |
| I10 | Causas de muerte y variantes de mensaje | Medio-alto | Bajo | Bajo | 5A, junto con el HUD |

---

## 2. Evaluación

El combate tower defense es **la capa más grande que se ha propuesto hasta ahora**. No es una variante de la simulación actual: añade enemigos, objetivos, daño, defensas, oleadas, botín y una economía nueva. Si se implementa junto con el árbol de tecnologías y el inventario, el riesgo de scope creep es alto.

La idea del radar como arma de doble filo es muy buena:

- Explorar más = ver más recursos y peligros.
- Más radar = más señal = más alimañas.
- Apagar el radar reduce la amenaza, pero detiene la exploración.
- El apagado/encendido de la fase 4 se convierte en una decisión táctica real.

El punto delicado es la **justicia**: un radio invisible que dispara ataques sin aviso se siente arbitrario. La solución no es mostrar el radio exacto, sino dar señales cualitativas antes y durante el primer contacto (ruido en la consola, interferencias, alimañas muertas en el perímetro, un aviso de “señal anómala”). El jugador debe poder aprender la regla por consecuencias, no por un manual.

También hay una deuda inmediata que esta fase expone:

- `draw_top_bar()` muestra **Cmp, E y O₂**, y omite agua y comida. La barra actual no refleja lo que mata.
- El juego muere por O₂, agua y comida (`ResourcePool.death_cause()`), no por energía.
- El inventario está partido entre `ResourcePool` (vitales) y `Stockpile` (materiales), y no hay un lugar único para consultar todo.
- Los mensajes de muerte son una sola cadena por causa (`death.o2`, `death.water`, `death.food`).

Con recursos de botín, el conteo actual no escala: añadir un campo por recurso a `Stockpile` obliga a tocar simulación, UI, guardado y balance cada vez.

---

## 3. Decisiones de diseño

### 3.1 Radar, exploración y amenaza oculta

- El radar es la **única fuente de exploración permanente**. Cables y paneles solares pueden dar visión local (mantenimiento), pero no deben marcar `explored` de forma permanente. Esto hace del radar una inversión con coste.
- Un radar activo emite una **señal oculta** con un radio mayor que su círculo de visión. El jugador ve la visión; no ve el radio de atracción.
- La presión de amenaza crece con: días transcurridos, radares activos, cobertura explorada y tiempo de exposición. Cuanto más avanza la partida, más llegan.
- Las alimañas aparecen en el borde de la señal y se dirigen al radar o al hábitat; atacan cables y módulos a su paso.
- Apagar un radar detiene la exploración y reduce la presión, pero no la elimina de inmediato: la amenaza tiene inercia (warm-up/cooldown) para que apagar/encender no sea gratis.
- Primer contacto con periodo de gracia y aviso diegético. Sin barra de “amenaza” visible al principio; sí registro en consola.

### 3.2 Combate tower defense

- **Combate automático.** El jugador no controla al astronauta ni apunta: coloca torretas, trampas y refuerzos, y gestiona energía y red. Esto conserva la fantasía de “consola del astronauta”.
- Primer slice: **1–2 tipos de alimaña**, una torreta y una trampa. Sin pathfinding global: la alimaña avanza hacia el radar/hábitat y ataca el primer cable o módulo que encuentra. Si se bloquea, ataca el bloqueo.
- Las rutas y la topología de cables importan: cortar un cable cambia el camino y puede aislar módulos. Más adelante se puede añadir un flow field si el mapa lo exige.
- Modelo de daño inicial: **eventos**, no HP por entidad. Una alimaña puede cortar un cable (se elimina) o dejar un módulo `OFFLINE`/dañado durante un tiempo. Reparar cuesta componentes. Si el modelo se queda corto, se añade HP en 5D.
- En 5B las alimañas **no matan directamente**: degradan la red y provocan fallos en cadena (sin energía, sin agua, sin O₂). La muerte directa por alimañas queda para 5D, cuando exista integridad del hábitat.
- Las oleadas escalan con días y radares; no con el número de módulos, para no castigar la construcción.

### 3.3 Exploración y botín

- El radar revela **puntos de interés**: pecios, nidos, depósitos raros. El jugador los selecciona y lanza una operación de salvamento desde la consola (coste en energía/componentes y tiempo). No hay desplazamiento del astronauta.
- El botín de exploración y de alimañas usa los mismos tipos de item, para que una receta no dependa de una sola fuente.
- Recursos nuevos propuestos (cada uno debe nacer con ≥2 fuentes y ≥2 usos):

| Item | Fuente 1 | Fuente 2 | Uso 1 | Uso 2 |
|------|----------|----------|-------|-------|
| Biomasa | Alimañas | Compost / invernadero | Fertilizante / comida | Investigación |
| Quitina | Alimañas | Nidos | Trampas / blindaje | Reparaciones |
| Aleación | Pecios | Reciclaje | Torretas / estructura | Reparaciones |
| Núcleo | Ruinas | Alimaña rara | Tecnología | Radio / final |

- La regla de la fase 4 se mantiene: un recurso nuevo no entra si nace con una sola fuente o un solo uso.

### 3.4 Inventario, conteo y barra superior

El cambio de conteo es un **refactor de datos**, no solo de UI:

- `ResourcePool` se queda para los vitales (O₂, energía, agua, comida), porque tienen consumo diario, muerte y días restantes.
- `Stockpile` se sustituye por un **`Inventory` genérico** con `ItemKind` (componentes, mineral, biomasa, quitina, aleación, núcleo…) y cantidades. Así agregar un item no obliga a añadir un campo nuevo.
- El almacenamiento deja de dar +40 a cada recurso. Los módulos de almacén aportan **capacidad de carga compartida** para materiales/botín; los vitales mantienen sus caps del hábitat. Evita que 8 recursos nuevos hereden +40 cada uno.
- La barra superior muestra **solo recursos críticos**, no materiales:
  - O₂, agua y comida son letales hoy.
  - La energía es crítica pero **no mata directamente** en el código actual; hoy solo limita módulos.
  - Propuesta: cuatro indicadores compactos (O₂, agua, comida, energía) o, si no caben, los 3 con menos días de reserva (dinámico) + un icono de energía. Los componentes y el botín se ven en la consola.
- La consola añade una pestaña **CARGA** con todos los items por categoría, cantidad y capacidad. El panel lateral sigue mostrando solo el contexto del tile/módulo.
- El guardado serializa el inventario por clave de item, con versión de esquema.

### 3.5 Causas de muerte y variantes

Hoy `ResourcePool.death_cause()` devuelve una clave única (`death.o2`, `death.water`, `death.food`). El game over muestra esa única línea. La propuesta:

- `DeathCause` con id, orden de prioridad y un pool de claves de variante.
- Elegir una variante al morir (aleatoria o determinista por run) y guardar causa + variante.
- El game over muestra: causa, variante y días sobrevividos. El modal debe partir líneas largas.
- No inventar causas que el código no pueda producir: la energía solo tendrá mensaje de muerte si se implementa el fallo de soporte vital.

| Causa | Disparador actual/propuesto | Variantes propuestas |
|-------|----------------------------|----------------------|
| Sed | Agua = 0 (actual) | “Te moriste de sed”, “Te secaste”, “Sin nada que beber moriste” |
| Asfixia | O₂ = 0 (actual) | “Te has ahogado”, “La agonía de no poder respirar te mató”, “El O₂ se agotó” |
| Inanición | Comida = 0 (actual) | “Moriste sin nada que comer”, “Te has muerto de hambre”, “La despensa quedó vacía” |
| Alimañas | Hábitat destruido (5D) | “Las alimañas rompieron el casco”, “El enjambre llegó al hábitat”, “Los cables cedieron” |
| Fallo de energía | 0 energía durante X horas (solo si se decide que mate) | “El soporte vital se apagó”, “Sin energía, todo se detuvo” |
| Frío / calor | Evento climático (fase posterior) | “La helada te venció”, “El calor colapsó el hábitat” |

La muerte por energía es una decisión pendiente: hoy el hábitat consume O₂/agua/comida aunque no haya energía, así que la energía no es letal. Si se quiere que lo sea, hay que definir una regla explícita de fallo del soporte vital y entonces sí mostrarla en la barra como lethal.

---

## 4. Matriz de recursos nuevos

| Recurso | Fuentes | Usos | Nota de balance |
|---------|---------|------|-----------------|
| Biomasa | Alimañas, compost | Fertilizante, investigación | Debe competir con comida, no ser comida gratis |
| Quitina | Alimañas, nidos | Trampas, blindaje, reparaciones | La fuente principal es el combate; el nido es la alternativa pasiva |
| Aleación | Pecios, reciclaje | Torretas, estructura, reparaciones | El pecio es finito; el reciclaje es sostenible pero caro |
| Núcleo | Ruinas, alimaña rara | Tecnología, radio/final | Recurso de progresión, no de construcción masiva |

---

## 5. Caminos posibles

| Camino | Qué hace | Pros | Contras |
|--------|----------|------|---------|
| A. Tower defense completo ya | Enemigos, pathfinding, oleadas, torres, loot y jefes de una vez | Se ve el sistema completo | Riesgo altísimo; tapa la fase 4 |
| B. Solo alimañas ambientales | Roen cables y consumen reservas, sin combate | Bajo riesgo, encaja con el concepto original | No cumple la idea de tower defense |
| C. Tower defense por capas | Primero inventario/HUD/muerte; luego un enemigo, una trampa y una torreta; después oleadas y loot | Valida el loop con coste controlado | Menos contenido inicial |

**Decisión: C.** El combate entra como capa, no como reemplazo del juego de gestión.

---

## 6. Riesgos y mitigaciones

| Riesgo | Prob. | Impacto | Mitigación |
|--------|-------|---------|------------|
| El combate se come el proyecto | Alta | Alto | Slice 5B con 1 enemigo, 1 torreta, 1 trampa |
| Radio invisible injusto | Alta | Alto | Avisos diegéticos, periodo de gracia, primer ataque tutorial |
| Pathfinding caro en 1024² | Media | Alto | Sin pathfinding global en 5B; seguir la red/objetivo |
| Inventario mal refactorizado rompe economía | Media | Alto | 5A aislado, tests de caps/consumo/guardado |
| Barra superior ilegible | Media | Medio | Iconos + 3/4 indicadores; materiales a consola |
| Mensajes de muerte no coinciden con la mecánica | Media | Medio | Catálogo ligado a `DeathCause`; tests de causa |
| Guardado incompatible al añadir items | Media | Medio | Versión de esquema y migración mínima |
| El jugador apaga radares y evita todo el combate | Media | Medio | Inercia de amenaza, cooldown y coste de exploración |
| Rendimiento en R36S con muchas entidades | Baja | Medio | Límite de alimañas activas; simulación por ticks |

---

## 7. Plan por slices

### Slice 5A — Inventario, HUD y muerte (sin combate)

- `ItemKind` + `Inventory` genérico; migrar componentes/mineral de `Stockpile`.
- Capacidad de carga compartida para materiales/botín.
- Conectar la barra superior de UI-1 a los vitales reales; componentes y botín a la consola.
- Conectar la pestaña CARGA de UI-2 al inventario genérico.
- `DeathCause` + catálogo de variantes y game over con causa/variante/días.
- Tests de caps, construcción, guardado y mensajes.

### Slice 5B — Radar, alimañas y primera defensa

- Radar como única exploración permanente; visión local de cables/solar sin marcar `explored`.
- Señal oculta, presión por días/radares y primer contacto con aviso.
- 1 tipo de alimaña: aparece en el borde de la señal, avanza al radar/hábitat y corta cables/deja módulos offline.
- 1 trampa y 1 torreta automática; energía y componentes como coste.
- Botín de alimaña (biomasa/quitina) y primer uso.

### Slice 5C — Oleadas, puntos de interés y más botín

- Oleadas escaladas, 2–3 enemigos, nidos/pecios y salvamento desde consola.
- Aleación/núcleo y sus usos.
- Mejoras de radar/torreta y reparaciones.
- Balance de capacidades y consumo.

### Slice 5D — Muerte directa, eventos y finales

- Integridad del hábitat y muerte por alimañas.
- Fallo de energía (si se decide que mate).
- Eventos climáticos y muerte por frío/calor.
- Radio, núcleo y finales.

---

## 8. Criterios de aceptación

- **5A:** la barra superior muestra los recursos letales (agua, O₂, comida) y energía; los materiales ya no ocupan la barra; la consola muestra todos los items con capacidad; el game over muestra causa + variante + días; guardar/cargar conserva inventario y causa.
- **5B:** apagar todos los radares detiene la exploración y reduce la presión; un radar activo atrae alimañas tras el periodo de gracia; una trampa mata/contiene; una torreta consume energía y dispara sola; un cable cortado se puede reconstruir.
- **5C:** existen al menos dos fuentes y dos usos para los cuatro items nuevos; un pecio/nido produce botín; las oleadas escalan con días/radares.
- **5D:** una alimaña puede destruir el hábitat y producir `death.pests`; un evento climático puede matar; el final se puede alcanzar.

---

## 9. Decisiones pendientes

1. ¿La energía debe matar? Recomendación: no directamente; es un multiplicador de riesgo. Si se hace letal, definir el tiempo de fallo y el mensaje.
2. ¿La comida sigue siendo letal? Recomendación: sí; es el recurso más claro de supervivencia.
3. Barra superior: ¿4 indicadores fijos o los 3 peores dinámicos + energía? Recomendación: 4 compactos; si no caben, dinámicos.
4. ¿Radar único explorador o visión local de cables/solar sin exploración permanente? Recomendación: lo segundo.
5. Radio invisible: ¿por radar o presión global? Recomendación: señal por radar + presión global por días/cobertura.
6. Pathfinding: ¿red de cables como camino o flow field? Recomendación: red/objetivo en 5B; flow field solo si hace falta.
7. Capacidad: ¿carga compartida o cap por item? Recomendación: compartida para materiales/botín.
8. ¿Muerte directa por alimañas en 5B o 5D? Recomendación: 5D, con integridad del hábitat.
9. ¿El botín se puede perder al morir? Recomendación: no en 5B; la partida termina y se reinicia.
10. ¿Los radares apagados siguen siendo atacables? Recomendación: sí, son estructuras; apagarlos reduce la atracción, no los vuelve invisibles.
