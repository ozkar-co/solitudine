# Plan de fase 4 — consola, tecnología y recursos

> **Decisión vigente:** 2026-10-28. Este documento manda sobre `ideas.md` para el próximo bloque de trabajo.
> Objetivo: convertir el sandbox actual en una progresión con decisiones sin romper el MVP ni la legibilidad en 640×480.
> **Siguiente etapa:** [plan-ui.md](plan-ui.md). La UI (layout, assets, consola y HUD) se adelanta; 4A se limita a apagado, guardado y tests.
> **Después:** [plan-fase5.md](plan-fase5.md) (alimañas, tower defense, botín, inventario y muerte). No abrir antes de cerrar 4A–4C.

---

## 1. Punto de partida real

Verificado en el código actual:

- Juego Pygame en la raíz, una sola entrada (`main.py`) y `Makefile` con `config`, `fetch`, `clean`, `dist`.
- Mapa 1024², cámara, niebla, construcción libre por cables, 9 tipos de módulo.
- Simulación por días de 48 s, energía proporcional, buffers, depósitos finitos y game over por O₂/agua/comida.
- 6 recursos: O₂, energía, agua, comida, mineral y componentes.
- UI de mapa + panel lateral de 168 px, modal de construcción, pausa y game over.
- **No hay** investigación, guardado, desgaste, eventos climáticos, apagado manual ni tests.

### Evaluación del pivote texto → GUI

El cambio de TUI/grafo abstracto a mapa 2D fue correcto para este proyecto:

- Aprovecha la pantalla 640×480 de la R36S y el mando.
- La distancia, el terreno y la exploración pasan a ser decisiones reales.
- La fantasía de “consola del astronauta” se mantiene si la UI sigue siendo de telemetría, no un juego de construcción genérico.

Lo que se perdió: la lectura instantánea de un grafo y la estética ASCII. No conviene volver atrás; conviene recuperar esa identidad en las pantallas de consola (tecnología, diagnóstico, alertas) y no en el mapa.

**Diagnóstico:** el cuello de botella ya no es el renderizado ni el mapa. Es la **progresión**: hay supervivencia y logística, pero pocas decisiones con consecuencias y ninguna forma de desbloquear el sistema. La fase 4 debe atacar eso.

---

## 2. Ideas registradas (2026-10-28)

| ID | Idea | Valor | Esfuerzo | Riesgo | Decisión |
|----|------|-------|----------|--------|----------|
| I1 | Mejorar la UI (panel, acciones, consola, legibilidad) | Alto | Medio | Medio | Entra primero, de forma incremental |
| I2 | Árbol de tecnologías con desbloqueos | Alto | Medio-alto | Alto (alcance, guardado) | Entra como slice pequeño, no como árbol completo |
| I3 | Cada recurso se usa para más de una cosa | Alto | Medio | Medio (balance) | Se implementa con tecnologías, sin inflar recursos |
| I4 | Cada recurso se obtiene de más de una forma | Alto | Medio | Medio (balance) | Se implementa con fuentes alternativas con coste |
| I5 | Encender/apagar módulos | Medio-alto | Bajo | Bajo-medio (explotos, visión) | Entra primero; es barato y mejora el control |

### Regla de los seis

Cada recurso debe terminar con al menos dos usos y dos fuentes. Un recurso nuevo no entra si nace con un solo uso o una sola fuente; los seis actuales se completan con tecnologías, no añadiendo recursos. La investigación no se guarda como recurso: es progreso de un laboratorio. Esto evita el “recurso #12 que solo sirve para una receta” y mantiene el foco en el balance.

---

## 3. Matriz actual de recursos

| Recurso | Fuentes actuales | Usos actuales | Hueco |
|---------|------------------|---------------|-------|
| O₂ | Reserva inicial, invernadero (+2/d) | Soporte vital | Una sola fuente sostenible; un solo uso |
| Energía | Panel solar | Casi todos los módulos | Una sola fuente; sin almacenamiento real |
| Agua | Extractor en agua/depósito | Soporte vital, invernadero | Una sola fuente; falta uso industrial |
| Comida | Invernadero | Soporte vital | Una sola fuente; un solo uso |
| Mineral | Mina sobre depósito | Fabricador | Una sola fuente; un solo uso |
| Componentes | Fabricador | Construcción | Una sola fuente; un solo uso |

### Matriz objetivo (fase 4, sin recursos nuevos)

| Recurso | Fuente 2 | Uso 2 | Tecnología |
|---------|----------|-------|------------|
| O₂ | Electrólisis (agua + energía) | Oxidante para nave (final) | Electrólisis / fase final |
| Energía | Batería (desplaza excedente solar a la noche); aerogenerador/RTG en 4D | Investigación, electrólisis, condensador | Batería / Energía |
| Agua | Condensador atmosférico (energía) | Electrólisis, refrigeración | Condensador / Electrólisis |
| Comida | Hidroponía / invernadero mejorado | Cebo de trampas, compost | Hidroponía / plagas |
| Mineral | Reciclaje de módulos demolidos | Construcción directa, reparaciones | Reciclaje |
| Componentes | Reciclaje de módulos | Investigación, kits de reparación | Reciclaje |

La comida es el recurso más difícil de dar un segundo uso sin añadir otro recurso. Se resuelve en la fase de plagas (cebo) o con compost; no se fuerza ahora.

---

## 4. Decisiones de diseño

### 4.1 Encendido/apagado: `enabled`, no un estado nuevo

`ModuleState` ya significa “construcción/conectividad”. Mezclar “apagado por el jugador” ahí rompe la intención del usuario cuando cambia la red.

- Añadir `Module.enabled: bool = True`.
- `module_active(mod, connected)` = `state == ONLINE` **y** conectado **y** `enabled`.
- El hábitat es `toggleable=False` y siempre está activo.
- Un módulo apagado: no produce, no consume energía, no aporta visión, no suma cap de almacén y no vacía su buffer.
- La UI debe mostrar “Apagado” y una marca visual en el mapa.
- Acción: **R1** sobre el módulo seleccionado. R1 está libre hoy.
- El estado `enabled` se guarda en la partida.

Consecuencia técnica: centralizar la comprobación en una sola función y usarla en `module_tick`, `logistics`, `vision` y `ui_panel`. No duplicar la condición.

### 4.2 Árbol de tecnología: DAG de datos, no un grafo libre

- 3 ramas iniciales: **Soporte** (O₂, agua, comida), **Energía** (generación, almacenamiento) y **Logística** (reciclaje, reparación, sensores).
- 2–3 niveles por rama. Nodos con prerrequisitos explícitos.
- Cada nodo declara: id, rama, nivel, coste en componentes, días de investigación y desbloqueos (módulo, receta o habilidad).
- Se investiga **un nodo a la vez**. El laboratorio debe estar en línea y con energía; si se apaga o desconecta, la investigación se pausa.
- El coste es **componentes + tiempo + energía de laboratorio**. No se crea un recurso “ciencia” todavía.
- El menú de construcción muestra las piezas bloqueadas en gris con su tecnología requerida, no las oculta.

El árbol se dibuja como **columnas navegables**, no como un grafo de nodos y líneas: en 640×480 y con mando, una lista jerárquica es más legible y más rápida de recorrer. La “sensación de consola” la da la pantalla completa, no un diagrama decorativo.

### 4.3 UI: mapa + panel + consola a pantalla completa

Se mantiene la estructura actual. No se rehace la UI desde cero.

- **Panel lateral:** scroll o paginación cuando la inspección no cabe; barra de acciones contextual; estado encendido/apagado; recursos con barra además del número.
- **Barra inferior:** acciones disponibles según contexto, no solo texto descriptivo.
- **Consola (SELECT):** overlay a pantalla completa con tres zonas: ramas, nodos y detalle. Pestañas para Tecnología / Registro / Ayuda.
- **Construcción:** agrupada por categorías y con candados visibles.
- **Mapa:** módulos apagados atenuados o rayados; alertas sobre el tile, no solo en el panel.

Wireframe de la consola:

```text
┌─────────────────────────────────────────────┐
│ CONSOLA > TECNOLOGÍA          Día 3  14h    │
├──────────────┬──────────────────┬───────────┤
│ RAMAS        │ NODOS            │ DETALLE   │
│ > Soporte    │ [x] Electrólisis │ Coste: 6  │
│   Energía    │ [ ] Condensador  │ Tiempo: 2d│
│   Logística  │ [ ] Reciclaje    │ Requiere: │
│              │                  │ Laboratorio│
│              │                  │ A=investigar│
├──────────────┴──────────────────┴───────────┤
│ L1/R1=rama  LJOY=navegar  A=investigar B=salir│
└─────────────────────────────────────────────┘
```

### 4.4 Guardado mínimo antes de un árbol grande

Sin persistencia, un árbol de tecnologías es una trampa: el jugador pierde horas de progreso al morir o cerrar.

- Guardado JSON versionado junto al ejecutable (`save.json`, ignorado por git).
- Guardar: día, recursos, stock, módulos, cables, enabled, tecnologías desbloqueadas, investigación activa y progreso.
- Auto-guardado al comenzar un día y al pausar; escritura atómica (temporal + `os.replace`).
- SQLite puede esperar; para una partida, JSON es suficiente y cumple “stdlib primero”.

### 4.5 Investigación y laboratorio

- Nuevo módulo **Laboratorio**, construible desde el inicio (sin tecnología previa) para evitar el huevo y la gallina.
- Consume energía y permite investigar; varias labs suman velocidad con rendimientos decrecientes o un tope, a decidir en balance.
- La investigación no avanza si la lab está apagada, desconectada o sin energía.
- El árbol inicial del slice: **4 tecnologías** (Electrólisis, Condensador, Reciclaje, Batería). El resto queda diseñado pero no implementado.

---

## 5. Caminos posibles

| Camino | Qué hace | Pros | Contras |
|--------|----------|------|---------|
| A. Contenido primero | Añadir muchos módulos, recursos y recetas ya | Se ve progreso rápido | Se rehace balance y UI; deuda técnica |
| B. Motor primero | Generalizar recetas, efectos y automatización | Base robusta | Riesgo de sobreingeniería; KISS |
| C. Vertical slice | UI/control + 4 tecnologías + 2–3 fuentes alternativas + guardado | Valida el loop completo | Menos contenido inicial |

**Decisión: C.** El proyecto necesita aprender si la progresión es divertida antes de invertir en un árbol de 30 nodos.

---

## 6. Riesgos y mitigaciones

| Riesgo | Prob. | Impacto | Mitigación |
|--------|-------|---------|------------|
| Scope creep (5 sistemas a la vez) | Alta | Alto | Slice cerrado; no-goals explícitos |
| UI ilegible en 3.5" | Media | Alto | Consola a pantalla completa, listas, probar en R36S |
| Fuentes alternativas trivializan el juego | Media | Alto | Cada fuente con coste/limitación distinta; tests de balance |
| Sin guardado, el árbol no es viable | Alta | Alto | Guardado JSON en el primer slice |
| `module_tick` se vuelve un `if/elif` gigante | Alta | Medio | Datos en `module_defs`/`tech_defs`; handlers solo para lo especial |
| Apagado rompe visión o energía | Media | Medio | Helper único `module_active`; test de regresión |
| Documentación y código divergen | Media | Medio | Actualizar `estado.md` al cerrar cada slice |
| Sin tests, la matriz de recursos explota | Alta | Medio | `unittest` headless para economía y toggle |
| Conflictos de input en consola | Media | Medio | `ui_input.input_policy()` + ayuda contextual |

---

## 7. Plan por slices

### Slice 4A — Control y guardado (después de UI-2)

- `Module.enabled` + helper `module_active()`.
- Acción R1 conectada a la UI ya construida; hábitat no toggleable.
- Guardado JSON mínimo.
- Tests: toggle no altera recursos, visión ni caps; guardado/carga conserva `enabled`.
- La barra superior, el panel con scroll y la consola ya vienen de [plan-ui.md](plan-ui.md); no duplicar ese trabajo aquí.

### Slice 4B — Tecnología mínima

- `tech_defs.py` con 4 nodos y sus prerrequisitos.
- `ResearchState` + módulo Laboratorio + progreso ligado a energía.
- Conectar la pestaña Tecnología de UI-2 a ramas, nodos, coste, progreso y bloqueos.
- Menú de construcción filtrado por desbloqueos, mostrando candados.
- Guardado de desbloqueos e investigación activa.

### Slice 4C — Matriz de recursos v1

- Electrolizador: agua + energía → O₂.
- Condensador: energía → agua.
- Reciclaje: demoler módulos devuelve parte de componentes/mineral.
- Batería: almacena energía (no solo cap de red).
- Actualizar la matriz: dos fuentes para O₂, energía, agua, mineral y componentes; dos usos para energía, agua, mineral y componentes. O₂ y comida completan su segundo uso en fases posteriores (nave y plagas).

### Slice 4D — Profundidad

- Plagas/trampas (comida como cebo).
- Desgaste y reparación con componentes.
- Eventos climáticos.
- Más nodos de tecnología, radio y finales.

### No-goals de esta fase

- Volver al grafo abstracto o a una TUI.
- Añadir recursos nuevos antes de cumplir la regla de los seis.
- Árbol gráfico de nodos y líneas.
- Nuevos biomas, combate, multijugador.
- Nuitka/PyInstaller (la distribución sigue siendo PortMaster + squashfs).
- Generalizar un motor de recetas: en 4A–4C cada módulo declara su flujo fijo en `module_defs.py`; se generaliza solo si aparece un módulo con dos recetas reales.
- Combate, alimañas y botín: fase 5. El modelo de visión/radar actual es provisional y cambiará allí.

---

## 8. Criterios de aceptación

- **4A:** R1 apaga/enciende el módulo seleccionado; un módulo apagado consume 0, produce 0 y no da visión; el hábitat no se puede apagar; guardar/cargar conserva el estado; test headless pasa.
- **4B:** la lab solo investiga si está online y con energía; una tecnología desbloquea una pieza en el menú; el árbol se navega con mando; guardar/cargar conserva desbloqueos y progreso.
- **4C:** existen al menos dos fuentes para O₂, energía, agua, mineral y componentes, y dos usos para energía, agua, mineral y componentes; cada fuente tiene una limitación real (energía, espacio, depósito finito o tecnología).
- **4D:** una plaga puede dañar un módulo, una trampa la contiene y el jugador puede reparar con componentes.

---

## 9. Decisiones pendientes de balance

1. Coste y consumo del laboratorio; ¿una lab o varias?
2. Coste/tiempo exacto de los 4 nodos del slice.
3. ¿La batería almacena energía por módulo o amplía el cap de red?
4. ¿El reciclaje devuelve un porcentaje fijo o depende de la tecnología?
5. ¿La comida se usa como cebo (plagas) o como compost? Recomendación: cebo, porque conecta con la fantasía de alimañas.
6. ¿Se puede cancelar una investigación? Recomendación: sí, sin reembolso, para evitar bloqueos.
7. Ubicación del guardado en R36S: junto al ejecutable; confirmar permisos de escritura.

---

## 10. Próximo paso concreto

Primero [plan-ui.md](plan-ui.md): UI-0, UI-1 y UI-2. La UI deja el panel, la barra y la consola listos.

Después, **Slice 4A** en este orden:

1. `Module.enabled` + `module_active()` y tests.
2. Acción R1 conectada a la UI existente.
3. Guardado JSON mínimo.

Después de 4A, playtest corto y recién entonces abrir 4B.
