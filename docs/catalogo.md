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
| Soporte | Invernadero, Lámpara, Electrolizador*, Condensador* |
| Logística | Cable, Fabricador, Almacén |
| Ciencia | Radar, Laboratorio* |
| Defensa* | Torreta, Trampa |

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
| `battery` | Batería | Energía | backlog | `bateria` | Almacenamiento de energía |
| `turret` / `trap` | Torreta / Trampa | Defensa | backlog | — | Combate |

## Números implementados (4B/4C)

| Módulo | Coste | Obra | Energía | Entrada | Salida |
|--------|-------|------|---------|---------|--------|
| Laboratorio | 10 Cmp | 2 d | 3 E/d | — | Investigación |
| Electrolizador | 8 Cmp | 1,5 d | 4 E/d | 6 agua/d | 4 O₂/d |
| Condensador | 8 Cmp | 1,5 d | 6 E/d | — | 5 agua/d |

Valores actuales; se ajustan en playtest. El resto de módulos actuales mantiene sus números de `config.py`.

## Tecnologías

- Todas requieren un **Laboratorio** construido.
- Un nodo a la vez; costo en componentes, tiempo en días; el laboratorio debe estar online, conectado y con energía.
- T1 cuesta 6 Cmp y 2 días; T2 cuesta 10 Cmp y 3 días (propuesta).
- Las mejoras de módulos se aplican **automáticamente** a los módulos existentes; no se reconstruyen.
- Una tecnología puede desbloquear un módulo, una acción (p. ej. reciclaje/demolición) o subir el tier de un módulo.
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
| `reciclaje` | Industria | 2 | `fabricacion_ii` | Desbloquea demolición con retorno de ~50% componentes | backlog |
| `solar_ii` | Energía | 1 | Laboratorio | Panel solar Mk II | backlog |
| `radar_ii` | Ciencia | 2 | `solar_ii` | Radar Mk II | backlog |
| `bateria` | Energía | 2 | `solar_ii` | Desbloquea `battery` | backlog |

## Reglas de upgrades

- Un módulo tiene **un solo ID**; “Mk II” es un tier, no un módulo nuevo.
- La tecnología desbloquea el tier máximo del módulo; todos los módulos de ese tipo usan las estadísticas nuevas en el siguiente tick.
- No se paga reconstrucción; el módulo existente se actualiza.
- El menú de construcción sigue mostrando una sola entrada por módulo; puede indicar `Mk II`.
- Los números de cada tier vivirán en `module_defs.py`; este catálogo define el efecto y la dependencia.

## Investigación y UI

- El laboratorio se construye desde el inicio.
- SELECT abre la pantalla de Tecnología: ramas, lista de nodos, coste, progreso, prerrequisito y bloqueo.
- A investiga el nodo seleccionado; B cierra. Sin pestañas vacías.
- El menú de construcción se agrupa por las categorías de arriba; las piezas bloqueadas se muestran en gris con su tecnología.
- Guardar: tecnologías desbloqueadas, tier por módulo, investigación activa y progreso.
