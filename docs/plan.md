# Plan

> Fuente única del roadmap. Catálogo de módulos/tecnologías: [catalogo.md](catalogo.md). Estado: [estado.md](estado.md). Código: [arquitectura.md](arquitectura.md). Juego: [diseno-juego.md](diseno-juego.md).
>
> Regla: un slice a la vez. 4B/4C están cerrados; toca playtest antes de abrir backlog.

## Norte

Gestión y supervivencia en un mapa 2D: red de módulos, recursos, luz y mantenimiento desde la consola del astronauta. La base ya es jugable; el siguiente problema es la **progresión**.

## Hecho (resumen)

- Mapa, cámara, niebla, cables, módulos, buffers, depósitos finitos y muerte por O₂/agua/comida.
- UI 640×480 en grilla de 16 px, sprites, zoom, minimapa, día/noche y lámpara.
- Apagado con **R1**, `Module.enabled` y guardado JSON automático.

## 4B — Tecnología mínima (hecho)

Objetivo: laboratorio, **2 tecnologías** y pantalla de Tecnología mínima. Nada de árbol grande ni consola multipestaña.

- **Laboratorio** construible desde el inicio.
- Investigación: un nodo a la vez; solo avanza si el laboratorio está online, conectado y con energía.
- Pantalla SELECT: lista de los 2 nodos implementados, coste, progreso y bloqueo.
- Menú de construcción por categorías (Energía, Extracción, Soporte, Logística, Ciencia) con piezas bloqueadas.
- Guardado de desbloqueos, investigación activa y progreso.
- Tecnologías del slice: `electrolisis` y `condensador` (ver [catalogo.md](catalogo.md)). Las mejoras Mk II quedan en backlog.
- Criterio: construir laboratorio, investigar, ver la pieza desbloqueada en su categoría, guardar/cargar y conservar progreso.

## 4C — Dos fuentes alternativas (hecho)

- Módulos: `electrolyzer` y `condenser` (efectos en [catalogo.md](catalogo.md)).
- Ambos se desbloquean con las tecnologías de 4B.
- La producción no depende de la luz; la lámpara es visual y solo consume energía.
- Criterio: O₂ y agua tienen dos fuentes; los módulos se detienen si falta energía; tests de tick y guardado.

## Siguiente: playtest

- Jugar 4B/4C en PC y R36S.
- Verificar que el laboratorio, la pantalla de Tecnología y las categorías se entienden sin explicación.
- Ajustar costes/tiempos y recién después elegir el siguiente backlog.

## Matriz de recursos

| Recurso | Fuentes actuales | Fuente nueva | Usos |
|---------|------------------|--------------|------|
| O₂ | Reserva inicial, invernadero | Electrolizador (4C) | Soporte vital |
| Agua | Extractor | Condensador (4C) | Soporte vital, invernadero, electrólisis |
| Energía | Solar | — | Casi todo |
| Comida | Invernadero | — | Soporte vital |
| Mineral | Mina | — | Fabricador |
| Componentes | Fabricador | — | Construcción |

Este slice solo cierra la segunda fuente de **O₂ y agua**. Regla: no se agrega un recurso nuevo hasta que los seis actuales tengan dos fuentes y dos usos.

## Backlog (no agendado)

- Reciclaje, batería y mejoras Mk II: ver [catalogo.md](catalogo.md).
- Alimañas ambientales primero; tower defense, botín, inventario y variantes de muerte después.
- UI: scroll, 9-slice, categorías, autotile, animaciones y overview solo si el contenido lo pide.
- Desgaste, eventos climáticos, radio y finales.

## No-goals

- Añadir recursos nuevos antes de completar la matriz.
- Generalizar un motor de recetas: cada módulo declara su flujo en `module_defs.py`.
- Crear un framework de UI o pantallas con pestañas vacías.
- Combate/tower defense como próxima etapa.
- Nuitka/PyInstaller: la distribución sigue siendo PortMaster + squashfs.

## Riesgos y decisiones

- **Scope creep**: 2 techs, 2 módulos, una pantalla. Todo lo demás es backlog.
- **UI**: no se toca el layout de 16 px ni se crea `ui_state`/`ui_widgets`.
- **Balance**: los números de 4B/4C son propuestas; el playtest manda.
- **Save**: versión 1; si cambia el esquema, subir versión.
- **Luz**: visual; la lámpara consume energía de noche proporcional a la oscuridad.
