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
- **A+A** abre el menú del módulo; encender/apagar, investigar, ver red o elegir combustible se eligen ahí, sin teclas dedicadas.
- Un módulo apagado no produce, no consume energía, no aporta visión, no suma capacidad de almacén y no emite luz.

## Recursos y supervivencia

- Recursos actuales: O₂, energía, agua, comida, mineral, componentes y chatarra.
- Nuevos (2026-11-05): madera, carbón, biodiésel y cristales. Madera y carbón alimentan el generador; el biodiésel se produce y se usa en el generador y en Cristalografía; los cristales quedan para v6.
- O₂, agua y comida son letales al llegar a cero; la energía es una restricción, pero puede matar indirectamente si falta agua para el condensador.
- Los depósitos son finitos; el agua tiene un depósito garantizado. La generación usa **anillos difusos**: densidad creciente con la distancia, rareza por recurso y cuota mínima por región. Cada partida nueva usa una **seed aleatoria `ABC-123`** (3 letras + 3 números); `--seed` la fija y el save la conserva. Bosques, carbón y cristales se generan ya. Detalle en [beta-txxt.md](beta-txxt.md).
- La regla de 2 fuentes / 2 usos es una heurística, no una obligación. La matriz completa está en [plan.md](plan.md).

## Red y logística

- Los módulos producen a buffers locales; la red tiene capacidad limitada.
- Los cables forman una **red logística única**: conectan módulos de cualquier tipo, sin redes separadas.
- El almacén general amplía los caps generales (+40), pero no energía ni O₂; no se puede apagar.
- La batería es un almacenamiento especializado (+100 energía) detrás de investigación; el tanque de O₂ y los tanques de agua quedan para v6.
- La energía se reparte proporcionalmente si falta; un módulo sin energía produce menos.
- Los productores se detienen al llenar su buffer o la red.

## Chatarra, ruinas y reciclador

- Las ruinas son tiles de 1×1 con 4-10 chatarra; hay 26 (2 garantizadas cerca del hábitat). Bloquean construcción y cables.
- Se seleccionan con **A** y se recogen con **A** otra vez; entran a la red con cap 30 (+40 por almacén).
- **B** sobre un cable seleccionado abre la confirmación de demolición. Los módulos se demolen desde su menú A+A; dejan una ruina con 0,6-0,9 de su equivalente mineral. El cable devuelve 1 Cmp.
- Cancelar una obra devuelve chatarra por los componentes pagados y el progreso (cap 0,9).
- El reciclador consume chatarra y agua para producir mineral; la tecnología `reciclaje` lo desbloquea.

## Luz y día/noche

- La noche dibuja un dithering sobre el terreno; la luz lo reduce.
- El hábitat ilumina desde el inicio; la lámpara amplía la zona iluminada.
- La lámpara consume energía solo de noche, proporcional a la oscuridad (máx. 4 E/día).
- La luz de la lámpara no cambia producción ni consumo; el panel solar sí depende del ciclo día/noche.

## Exploración e investigación

- Solo el radar explora de forma permanente; el resto da visión local.
- La investigación desbloquea módulos. Hoy el árbol se limita por recursos y laboratorio; a futuro tendrá prerrequisitos y tecnologías que solo desbloquean otras tecnologías.
- Tecnologías de fase 5: Fotovoltaica, Minería de carbón, Cristalografía y Almacenamiento especializado.
- Exploración avanzada, alimañas, botín y combate están en backlog.

## Controles

| Acción | PC (`--dev`) | Mando |
|--------|--------------|-------|
| Mover cursor | WASD | L-stick / DPAD |
| Mover cámara | Flechas | R-stick |
| Seleccionar / aceptar | E o J | A |
| Recoger chatarra de una ruina | E para seleccionar, E otra vez | A para seleccionar, A otra vez |
| Abrir menú de módulo | E otra vez sobre el módulo | A otra vez sobre el módulo |
| Elegir acción del menú | Arriba/Abajo + E | DPAD / L-stick + A |
| Demoler cable o cancelar obra | Esc o K sobre el cable seleccionado | B sobre el cable seleccionado |
| Confirmar demolición/cancelación | E | A |
| Acción especial (investigar, ver red, encender/apagar, demoler) | desde el menú A+A | desde el menú A+A |
| Construir | Tab | Y |
| Cambiar capa | Q | X |
| Cancelar | Esc o K | B |
| Cambiar categoría (menú de construcción) | A/D (o L-stick) | DPAD / L-stick |
| Zoom | 1 / 2 | L1/L2 |
| Minimapa | 3 | R2 |
| Acelerar tiempo (dev) | T | — |
| Iniciar partida (pantalla de carga) | Enter | START |
| Pausa / créditos | Enter, luego menú (Continuar/Créditos/Nueva partida/Salir) | START, luego menú |
| Salir | Backspace+Enter | SELECT+START |

> **Controles PC implementados (2026-11-05):** `1/2` zoom, `Tab` construir, `E` aceptar, `Q` recursos, `Esc` B, `J/K` duplicados de A/B; `3` minimapa, `4` libre, `T` acelera el tiempo en dev. Apagar/demoler módulos pasan por el menú A+A; B queda para cables. Ver [beta-txxt.md](beta-txxt.md).

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
- Pantalla de red (estación de monitoreo): producción y consumo en dos columnas, con icono + nombre de cada recurso, energía y estado de módulos.
- Modales anchos y unificados: título, subtítulo, columnas, scroll y ayuda; construcción, red, tecnología, créditos, pausa, demolición y game over comparten `draw_modal`.
- Menú de pausa con Continuar/Créditos; créditos con scroll y easter egg.

## Implementado / planificado

- **Trampa de peces (implementada):** módulo barato sobre agua, conectado por cable; produce solo de noche, con una tirada por hora (0 permitido) y ~3 comida/noche en promedio, y se detiene si el agua se agota. Al demoler no deja ruina: da chatarra directa.
- **Invernadero (implementado):** 10 Cmp; 6 comida/d + 3 O₂/d.
- **Procesador de biodiésel (implementado):** 4 Cmp; 4 comida/d + 2 agua/d + 2 E/d → 1 biodiésel/d.
- **Estación de monitoreo (implementada):** 6 Cmp, 2 E/d; online y conectada desbloquea la pantalla de red.
- **Extractores de carbón/cristal (implementados):** carbón 3 E/d → 6/d con Minería de carbón; cristales 4 E/d → 2/d con Cristalografía; placement sobre su depósito.
- **Generador eléctrico (implementado):** desde el inicio, apagado y sin combustible; 1 unidad/día → 5/12/20 E/d con madera/carbón/biodiésel.
- **Batería (implementada):** +100 cap de energía con Almacenamiento especializado; no reemplaza al almacén general.
- **Agua y radar (implementado):** depósito garantizado + anillos difusos finitos; el radar encuentra todo y es la exploración permanente.
- **Bosques y cristales (implementados):** bosque cercano garantizado (bloquea construcción, A tala y da madera, deja brotes), carbón en el borde de lo explorado y cristales en grupos de 2-3 puntos dispersos (4-5 los más grandes). Carbón y cristales ya tienen extractores; sus usos avanzados se definirán después.

## Backlog

- Mejoras Mk II, alimañas ambientales, tower defense, botín, inventario y variantes de muerte.
- Desgaste, eventos climáticos, radio y finales.
- Pulido de UI (9-slice, autotile, overview); las animaciones de menú ya están decididas.
- Cristales (usos), tanque de O₂, tanques especializados de agua y combate/eventos están planificados para v6 en [plan.md](plan.md). Trampa, mundo 2048/anillos, bosques/carbón, generador y batería ya están implementados.
