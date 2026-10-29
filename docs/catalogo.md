# Catálogo — módulos, categorías y tecnologías

> **Fuente única** para IDs, categorías, dependencias y efectos de módulos/tecnologías.
> Si algo no está aquí, no existe en el plan. El código (`module_defs.py`, y luego `tech_defs.py`) debe reflejar este catálogo; si divergen, se corrige el código.
>
> Estado: `hecho` (en código) o `backlog` (sin fecha).

## Categorías del menú de construcción

| Categoría | Módulos |
|-----------|---------|
| Energía | Panel solar, Batería* |
| Extracción | Extractor de agua, Mina |
| Soporte | Invernadero, Lámpara, Electrolizador, Condensador, Trampa de peces* |
| Logística | Cable, Fabricador, Almacén, Reciclador |
| Ciencia | Radar, Laboratorio |
| Defensa* | Torreta, Trampa de defensa |

`*` planeado o backlog. Defensa no aparece hasta que exista combate. El hábitat no es construible.

## Módulos

| ID | Nombre | Categoría | Estado | Tecnología | Mejora automática |
|----|--------|-----------|--------|------------|-------------------|
| `habitat` | Hábitat | Soporte | hecho | — | — |
| `cable` | Cable | Logística | hecho | — | — |
| `solar` | Panel solar | Energía | hecho | `solar_ii` | Mk II: +50% producción |
| `extractor` | Extractor de agua | Extracción | hecho | `extraccion_ii` | Mk II: +25% agua, −20% energía |
| `mine` | Mina | Extracción | hecho | `extraccion_ii` | Mk II: +25% mineral, −20% energía |
| `greenhouse` | Invernadero | Soporte | hecho | `agricultura_ii` | Mk II: +25% comida/O₂, −20% agua |
| `fabricator` | Fabricador | Logística | hecho | `fabricacion_ii` | Mk II: +25% componentes, −15% mineral |
| `storage` | Almacén | Logística | hecho | `almacenamiento_ii` | Mk II: +50% capacidad de red |
| `radar` | Radar | Ciencia | hecho | `radar_ii` | Mk II: +4 radio, −10% energía |
| `lamp` | Lámpara | Soporte | hecho | `iluminacion_ii` | Mk II: +2 radio, −25% energía |
| `laboratory` | Laboratorio | Ciencia | hecho | — | — |
| `electrolyzer` | Electrolizador | Soporte | hecho | `electrolisis` | Agua + energía → O₂ |
| `condenser` | Condensador | Soporte | hecho | `condensador` | Energía → agua |
| `fish_trap` | Trampa de peces | Soporte | backlog | — | 1-2 comida/noche sobre agua; se detiene si el agua se agota |
| `recycler` | Reciclador | Logística | hecho | `reciclaje` | Chatarra → mineral (ratio 0,9; 5% componentes) |
| `battery` | Batería | Energía | backlog | `bateria` | Cap de energía; el almacén deja de dar cap de energía |
| `turret` / `trap` | Torreta / Trampa de defensa | Defensa | backlog | — | Combate |

El cable forma una **red logística única**: conecta módulos de cualquier tipo, sin redes separadas. El almacén no se puede apagar.

## Números implementados (2026-10-29)

| Módulo | Coste | Obra | Energía | Entrada | Salida |
|--------|-------|------|---------|---------|--------|
| Hábitat | — | — | 8 E/d | 10 O₂/d · 10 agua/d · 8 comida/d | Soporte vital |
| Panel solar | 5 Cmp | 1 d | — | — | 12 E/d (solo 6-18 h) |
| Extractor de agua | 6 Cmp | 1 d | 2 E/d | — | 12 agua/d |
| Mina | 4 Cmp | 1,5 d | 3 E/d | — | 8 mineral/d |
| Invernadero | 8 Cmp | 1,5 d | 3 E/d | 4 agua/d | 10 comida/d + 2 O₂/d (O₂ requiere agua) |
| Fabricador | 5 Cmp + 2 mineral | 2 d | 4 E/d | 6 mineral/d | 4 componentes/d |
| Almacén | 5 Cmp | 1 d | — | — | +40 a los caps de red (hoy incluye energía; planificado: solo no-energía) |
| Radar | 8 Cmp | 1,5 d | 12 E/d | — | Exploración permanente |
| Lámpara | 6 Cmp | 1 d | 0-4 E/d (noche) | — | Luz |
| Laboratorio | 8 Cmp | 1,5 d | 3 E/d | — | Investigación |
| Electrolizador | 6 Cmp | 1 d | 4 E/d | 6 agua/d | 8 O₂/d |
| Condensador | 8 Cmp | 1,5 d | 6 E/d | — | 8 agua/d |
| Reciclador | 3 Cmp | 0,5 d | 1 E/d | 4 chatarra/d · 0,5 agua/d | 3,6 mineral/d + 0,2 Cmp/d |

Valores actuales de playtest. Cualquier ajuste se refleja en `config.py` y en esta tabla.

> **Coste multi-material activo:** el Fabricador cuesta **5 Cmp + 2 mineral**; la mina sigue en componentes para no bloquear el arranque. La chatarra tiene cap 30 (+40 por almacén) y las ruinas dan 4-10 por tile.

## Tecnologías

- Todas requieren un **Laboratorio** construido.
- Un nodo a la vez; coste multi-material (`Cost`), tiempo en días; el laboratorio debe estar online, conectado y con energía.
- T1 cuesta 4 Cmp y 1,5 días; T2 base cuesta 10 Cmp y 3 días (propuesta). `reciclaje` es T1 provisional: 5 chatarra + 2 Cmp + 1 mineral y 2 días.
- Las mejoras de módulos se aplican **automáticamente** a los módulos existentes; no se reconstruyen.
- Una tecnología puede desbloquear un módulo, una acción (p. ej. reciclaje) o subir el tier de un módulo.
- Varios laboratorios activos suman velocidad de investigación; cada uno consume energía.

| ID | Rama | Tier | Requiere | Efecto | Estado |
|----|------|------|----------|--------|--------|
| `electrolisis` | Soporte | 1 | Laboratorio | Desbloquea `electrolyzer` | hecho |
| `condensador` | Soporte | 1 | Laboratorio | Desbloquea `condenser` | hecho |
| `agricultura_ii` | Soporte | 2 | `electrolisis` | Invernadero Mk II | backlog |
| `iluminacion_ii` | Soporte | 2 | `condensador` | Lámpara Mk II | backlog |
| `extraccion_ii` | Industria | 1 | Laboratorio | Extractor y Mina Mk II | backlog |
| `fabricacion_ii` | Industria | 2 | `extraccion_ii` | Fabricador Mk II | backlog |
| `almacenamiento_ii` | Industria | 2 | `extraccion_ii` | Almacén Mk II | backlog |
| `reciclaje` | Industria | 1* | Laboratorio | Desbloquea `recycler`; la demolición ya existe desde el día 0 | hecho |
| `solar_ii` | Energía | 1 | Laboratorio | Panel solar Mk II | backlog |
| `radar_ii` | Ciencia | 2 | `solar_ii` | Radar Mk II | backlog |
| `bateria` | Energía | 2 | `solar_ii` | Desbloquea `battery` (cap de energía) | backlog |

`*` `reciclaje` queda en T1 hasta que exista el árbol T2; entonces se reubica en Industria con su prerrequisito.

## Reglas de upgrades

- Un módulo tiene **un solo ID**; “Mk II” es un tier, no un módulo nuevo.
- La tecnología desbloquea el tier máximo del módulo; todos los módulos de ese tipo usan las estadísticas nuevas en el siguiente tick.
- No se paga reconstrucción; el módulo existente se actualiza.
- El menú de construcción sigue mostrando una sola entrada por módulo; puede indicar `Mk II`.
- Los números de cada tier vivirán en `module_defs.py`; este catálogo define el efecto y la dependencia.

## Investigación y UI

- El laboratorio se construye desde el inicio.
- Con el laboratorio activo e inspeccionado, A otra vez abre la pantalla de Tecnología; SELECT queda libre. Incluye ramas, lista de nodos, coste, progreso, prerrequisito y bloqueo.
- A investiga el nodo seleccionado; B cierra. Sin pestañas vacías.
- El menú de construcción usa pestañas por categoría; las categorías vacías se ocultan y las piezas bloqueadas/no pagables se muestran en gris; las bloqueadas dicen “Investigar”. Cada módulo muestra descripción y flujo produce/consume.
- Guardar: tecnologías desbloqueadas, tier por módulo, investigación activa, progreso, día de construcción, coste pagado (`cost_paid`) de cada obra, ruinas y contadores de reciclaje.
