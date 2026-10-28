# Plan

> Única fuente del roadmap. Estado actual: [estado.md](estado.md). Código: [arquitectura.md](arquitectura.md). Juego: [diseno-juego.md](diseno-juego.md).
>
> Regla: un slice a la vez. El backlog no se abre hasta cerrar 4B/4C y hacer un playtest corto.

## Norte

Gestión y supervivencia en un mapa 2D: red de módulos, recursos, luz y decisiones de mantenimiento desde la consola del astronauta. La base ya es jugable; el siguiente problema es la **progresión**.

## Hecho (resumen)

- Mapa 1024², cámara, niebla, cables, módulos, buffers, depósitos finitos y muerte por O₂/agua/comida.
- UI 640×480 en grilla de 16 px, sprites, zoom 16/32/48, minimapa, día/noche y lámpara.
- Apagado con **R1**, `Module.enabled` y guardado JSON automático.
- El detalle está en [estado.md](estado.md).

## 4B — Tecnología mínima (siguiente)

Objetivo: un laboratorio, **2 tecnologías** y una pantalla de tecnología mínima. Nada de árbol grande ni consola multipestaña.

- **Laboratorio**: construible desde el inicio. Coste 10 Cmp, 2 días, 3 E/día.
- **Investigación**: un nodo a la vez; solo avanza si el laboratorio está online, conectado y con energía.
- **Pantalla**: SELECT abre una lista de 2 nodos con coste, progreso y bloqueo. DPAD navega, A investiga, B sale.
- **Desbloqueo**: el menú de construcción muestra la pieza bloqueada en gris hasta investigar.
- **Guardado**: desbloqueos, investigación activa y progreso.

| Tecnología | Efecto | Coste | Días | Requisito |
|------------|--------|-------|------|-----------|
| Electrólisis | Desbloquea **Electrolizador** | 6 Cmp | 2 | Laboratorio |
| Condensador | Desbloquea **Condensador** | 6 Cmp | 2 | Laboratorio |

Criterio de cierre: puedo construir el laboratorio, investigar una tecnología, ver la pieza desbloqueada, guardar/cargar y conservar el progreso.

## 4C — Dos fuentes alternativas (después de 4B)

| Módulo | Coste | Obra | Energía | Entrada | Salida |
|--------|-------|------|---------|---------|--------|
| Electrolizador | 8 Cmp | 1,5 d | 4 E/d | 6 agua/d | 4 O₂/d |
| Condensador | 8 Cmp | 1,5 d | 6 E/d | — | 5 agua/d |

- La producción **no depende de la luz**; la lámpara es visual y solo consume energía.
- Valores provisionales: se ajustan en playtest.
- Criterio de cierre: O₂ y agua tienen dos fuentes; los módulos se detienen si falta energía; tests de tick y guardado.

## Matriz de recursos

| Recurso | Fuentes actuales | Fuente nueva | Usos |
|---------|------------------|--------------|------|
| O₂ | Reserva inicial, invernadero | Electrolizador (4C) | Soporte vital |
| Agua | Extractor | Condensador (4C) | Soporte vital, invernadero, electrólisis |
| Energía | Solar | — | Casi todo |
| Comida | Invernadero | — | Soporte vital |
| Mineral | Mina | — | Fabricador |
| Componentes | Fabricador | — | Construcción |

Este slice solo cierra la segunda fuente de **O₂ y agua**. El resto queda para backlog. Regla: no se agrega un recurso nuevo hasta que los seis actuales tengan dos fuentes y dos usos.

## Backlog (no agendado)

- **Reciclaje**: idea para una tecnología que, al demoler un módulo, devuelva ~50% de su coste en componentes. **No está en 4B/4C** porque hoy no existe una acción de demolición. Se retoma cuando exista retirar módulos.
- **Batería** y otras fuentes de energía.
- **Alimañas ambientales** (roer cables) primero; tower defense, botín, inventario y variantes de muerte mucho después.
- **UI**: scroll del panel, 9-slice, categorías de construcción, autotile, animaciones y overview. Solo si el contenido lo pide.
- Desgaste, eventos climáticos, radio y finales.

## No-goals

- Añadir recursos nuevos antes de completar la matriz.
- Generalizar un motor de recetas: cada módulo declara su flujo en `module_defs.py`.
- Crear un framework de UI o pantallas con pestañas vacías.
- Combate/tower defense como próxima etapa.
- Nuitka/PyInstaller: la distribución sigue siendo PortMaster + squashfs.

## Riesgos y decisiones

- **Scope creep**: 2 techs, 2 módulos, una pantalla. Todo lo demás es backlog.
- **UI**: no se toca el layout 16 px ni se crea `ui_state`/`ui_widgets` hasta que duela.
- **Balance**: los números de 4B/4C son propuestas; el playtest manda.
- **Save**: versión 1; si cambia el esquema, subir versión.
- **Luz**: visual; la lámpara consume energía de noche proporcional a la oscuridad.
