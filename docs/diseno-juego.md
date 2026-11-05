# Diseño del juego

> Este documento describe el juego. Roadmap: [plan.md](plan.md). Catálogo de módulos/tecnologías: [catalogo.md](catalogo.md). Código: [arquitectura.md](arquitectura.md).

## Concepto

Eres el astronauta de **NEP-325**, atrapado en un hábitat de un planeta hostil. No sales: supervisas máquinas, cables, recursos y luz desde una consola. La dificultad es gestionar una red que crece y falla, no controlar un personaje.

## Loop

1. Explorar con el radar.
2. Construir módulos y cablear la red.
3. Producir y almacenar recursos.
4. Sobrevivir a O₂, agua y comida.
5. Investigar para desbloquear mejores fuentes.
6. Repetir con una red más grande y más frágil.

## Mapa y módulos

- Mapa parametrizable con default **2048×2048** (`--world-size`/`SOLITUDINE_WORLD_SIZE`); cámara con zoom entero (16/32/48 px).
- Los módulos y sus categorías están en [catalogo.md](catalogo.md).
- Todo se conecta por cables desde el hábitat. Sin conexión, el módulo queda offline.
- **R1** apaga/enciende el módulo seleccionado (excepto el hábitat).
- Un módulo apagado no produce, no consume energía, no aporta visión, no suma capacidad de almacén y no emite luz.

## Recursos y supervivencia

- Recursos actuales: O₂, energía, agua, comida, mineral, componentes y chatarra.
- Nuevos (2026-11-05): madera, carbón, combustible/biodiésel (producido) y cristales; ya están en la generación y en el pool, aunque carbón/cristal todavía no se puedan extraer.
- O₂, agua y comida son letales al llegar a cero; la energía es una restricción, pero puede matar indirectamente si falta agua para el condensador.
- Los depósitos son finitos; el agua tiene un depósito garantizado. La generación usa **anillos difusos**: densidad creciente con la distancia, rareza por recurso y cuota mínima por región; la seed se guarda. Bosques, carbón y cristales se generan ya. Detalle en [beta-txxt.md](beta-txxt.md).
- La regla de 2 fuentes / 2 usos es una heurística, no una obligación. La matriz completa está en [plan.md](plan.md).

## Red y logística

- Los módulos producen a buffers locales; la red tiene capacidad limitada.
- Los cables forman una **red logística única**: conectan módulos de cualquier tipo, sin redes separadas.
- El almacén amplía la capacidad de la red y no se puede apagar.
- Planificado: el almacén deja de dar cap de energía y la batería pasa a ser el reservorio de energía; los tanques especializados quedan para más adelante.
- La energía se reparte proporcionalmente si falta; un módulo sin energía produce menos.
- Los productores se detienen al llenar su buffer o la red.

## Chatarra, ruinas y reciclador

- Las ruinas son tiles de 1×1 con 4-10 chatarra; hay 26 (2 garantizadas cerca del hábitat). Bloquean construcción y cables.
- Se seleccionan con **A** y se recogen con **A** otra vez; entran a la red con cap 30 (+40 por almacén).
- **B** sobre un módulo/cable seleccionado abre la confirmación de demolición; el módulo deja una ruina con 0,6-0,9 de su equivalente mineral y el cable devuelve 1 Cmp.
- Cancelar una obra devuelve chatarra por los componentes pagados y el progreso (cap 0,9).
- El reciclador consume chatarra y agua para producir mineral; la tecnología `reciclaje` lo desbloquea.

## Luz y día/noche

- La noche dibuja un dithering sobre el terreno; la luz lo reduce.
- El hábitat ilumina desde el inicio; la lámpara amplía la zona iluminada.
- La lámpara consume energía solo de noche, proporcional a la oscuridad (máx. 4 E/día).
- La luz de la lámpara no cambia producción ni consumo; el panel solar sí depende del ciclo día/noche.

## Exploración e investigación

- Solo el radar explora de forma permanente; el resto da visión local.
- La investigación desbloquea módulos; el laboratorio y las tecnologías de soporte/reciclaje ya están implementados. La trampa de peces y la comida recurrente ya están implementadas; el próximo paso es la UX de red y módulos (etapa 4).
- Exploración avanzada, alimañas, botín y combate están en backlog.

## Controles

| Acción | PC (`--dev`) | Mando |
|--------|--------------|-------|
| Mover cursor | WASD | L-stick / DPAD |
| Mover cámara | Flechas | R-stick |
| Seleccionar / aceptar | E o J | A |
| Recoger chatarra de una ruina | E para seleccionar, E otra vez | A para seleccionar, A otra vez |
| Demoler módulo/cable o cancelar obra | Esc o K sobre la celda seleccionada | B sobre la celda seleccionada |
| Confirmar demolición/cancelación | E | A |
| Acción especial del módulo (Tecnología en laboratorio) | E otra vez sobre el módulo | A otra vez sobre el módulo |
| Construir | Tab | Y |
| Cambiar capa | Q | X |
| Cancelar | Esc o K | B |
| Cambiar categoría (menú de construcción) | A/D (o L-stick) | DPAD / L-stick |
| Zoom | 1 / 2 | L1/L2 |
| Apagar/encender (excepto hábitat/almacén) | 4 (temporal) | R1 |
| Minimapa | 3 | R2 |
| Acelerar tiempo (dev) | T | — |
| Iniciar partida (pantalla de carga) | Enter | START |
| Pausa / créditos | Enter, luego menú | START, luego menú |
| Salir | Backspace+Enter | SELECT+START |

> **Remapeo PC implementado (2026-11-05):** `1/2` zoom, `Tab` construir, `E` aceptar, `Q` recursos, `Esc` B, `J/K` duplicados de A/B; `3` minimapa, `4` apagar/encender (temporal hasta el menú A+A), `T` acelera el tiempo en dev. Apagar/demoler pasan al menú A+A en la etapa 4. Ver [beta-txxt.md](beta-txxt.md).

## UI

- 640×480, grilla de 16 px, fuente Pixel Operator (con VT323 como fallback) y sprites propios. El terreno alterna `ground_00`/`ground_01` y rotaciones de 90° por hash de coordenada; la costa usa un set rotable: lado, inner/outer, U, paralelo, isla y combinación inner+outer.
- Barra superior: O₂, agua, comida y energía, con nombre y `x/y`.
- Modo recursos (X): los once recursos con nombre y cantidad/cap, incluidos madera, carbón, combustible y cristales.
- Panel lateral: estado, descripción, producción/consumo, buffer, reserva, día de construcción y contadores del reciclador.
- Minimapa con región explorada, módulos, cables, ruinas y viewport.
- Menú de construcción por pestañas (**Energía, Extracción, Soporte Vital, Red Logística, Investigación**; Defensa se oculta hasta combate); categorías vacías ocultas. Cada módulo es una tarjeta horizontal con icono, borde/fondo propio, coste multi-material, faltantes, descripción y flujo produce/consume; la seleccionada se resalta en ámbar. El modal tiene scroll vertical animado para N tarjetas y el selector de categorías es circular, con slide/fade, la selección centrada y las etiquetas difuminadas hacia los bordes.
- Ruinas dibujadas en el mapa y modal de demolición/cancelación con confirmación A/B.
- Badges de modo/pausa y celda seleccionada; X cambia capa también en modo colocar.
- Consola de tecnología: una pantalla simple, sin pestañas vacías.
- Menú de pausa con Continuar/Créditos; créditos con scroll y easter egg.

## Implementado / planificado

- **Trampa de peces (implementada):** módulo barato sobre agua, conectado por cable; produce solo de noche, con una tirada por hora (0 permitido) y ~3 comida/noche en promedio, y se detiene si el agua se agota. Al demoler no deja ruina: da chatarra directa.
- **Invernadero (implementado):** 10 Cmp; 6 comida/d + 3 O₂/d.
- **Procesador de biodiésel (implementado):** 4 Cmp; 4 comida/d + 2 agua/d + 2 E/d → 1 combustible/d.
- **Batería (planificada):** el almacén deja de dar cap de energía; la batería pasa a ser el reservorio de energía.
- **Agua y radar (implementado):** depósito garantizado + anillos difusos finitos; el radar encuentra todo y es la exploración permanente.
- **Bosques y cristales (implementados):** bosque cercano garantizado (bloquea construcción, A tala y da madera, deja brotes), carbón en el borde de lo explorado y cristales en grupos de 2-3 puntos dispersos (4-5 los más grandes). Sus usos se definirán después.

## Backlog

- Mejoras Mk II, alimañas ambientales, tower defense, botín, inventario y variantes de muerte.
- Desgaste, eventos climáticos, radio y finales.
- Pulido de UI (9-slice, autotile, overview); las animaciones de menú ya están decididas.
- Batería y la extracción/uso de carbón/cristal están planificados en [plan.md](plan.md), no en este backlog. Trampa, mundo 2048/anillos y bosques/cristales ya están implementados.
