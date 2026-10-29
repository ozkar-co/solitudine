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

- Mapa de 1024×1024 tiles; cámara con zoom entero (16/32/48 px).
- Los módulos y sus categorías están en [catalogo.md](catalogo.md).
- Todo se conecta por cables desde el hábitat. Sin conexión, el módulo queda offline.
- **R1** apaga/enciende el módulo seleccionado (excepto el hábitat).
- Un módulo apagado no produce, no consume energía, no aporta visión, no suma capacidad de almacén y no emite luz.

## Recursos y supervivencia

- Recursos actuales: O₂, energía, agua, comida, mineral y componentes.
- Planificados: chatarra (intermedio), madera/biomasa, cristal y biodiésel (producido).
- O₂, agua y comida son letales al llegar a cero; la energía es una restricción, pero puede matar indirectamente si falta agua para el condensador.
- Los depósitos de agua/mineral son finitos; hoy hay un depósito de agua garantizado y se planifican depósitos RNG.
- La regla de 2 fuentes / 2 usos es una heurística, no una obligación. La matriz completa está en [plan.md](plan.md).

## Red y logística

- Los módulos producen a buffers locales; la red tiene capacidad limitada.
- Los cables forman una **red logística única**: conectan módulos de cualquier tipo, sin redes separadas.
- El almacén amplía la capacidad de la red y no se puede apagar.
- Planificado: el almacén deja de dar cap de energía y la batería pasa a ser el reservorio de energía; los tanques especializados quedan para más adelante.
- La energía se reparte proporcionalmente si falta; un módulo sin energía produce menos.
- Los productores se detienen al llenar su buffer o la red.

## Luz y día/noche

- La noche dibuja un dithering sobre el terreno; la luz lo reduce.
- El hábitat ilumina desde el inicio; la lámpara amplía la zona iluminada.
- La lámpara consume energía solo de noche, proporcional a la oscuridad (máx. 4 E/día).
- La luz de la lámpara no cambia producción ni consumo; el panel solar sí depende del ciclo día/noche.

## Exploración e investigación

- Solo el radar explora de forma permanente; el resto da visión local.
- La investigación desbloquea módulos; el laboratorio y las 2 tecnologías del primer slice ya están implementados. El próximo paso es el playtest.
- Exploración avanzada, alimañas, botín y combate están en backlog.

## Controles

| Acción | PC (`--dev`) | Mando |
|--------|--------------|-------|
| Mover cursor | Flechas / WASD | L-stick / DPAD |
| Mover cámara | Arrastrar con botón medio / right stick | R-stick |
| Seleccionar celda | A / Enter | A |
| Acción especial del módulo (Tecnología en laboratorio) | A otra vez sobre el módulo | A otra vez sobre el módulo |
| Construir | Y | Y |
| Cambiar capa | X | X |
| Cancelar | B / Esc | B |
| Cambiar categoría (menú de construcción) | Izquierda/Derecha | DPAD / L-stick |
| Zoom | L1/L2 (teclas Q/E o [/]) | L1/L2 |
| Apagar/encender (excepto hábitat/almacén) | R1 | R1 |
| Minimapa | R2 | R2 |
| Iniciar partida (pantalla de carga) | START | START |
| Pausa / créditos | START, luego menú | START, luego menú |
| Salir | SELECT+START | SELECT+START |

## UI

- 640×480, grilla de 16 px, fuente VT323 y sprites propios.
- Barra superior: O₂, agua, comida y energía, con nombre y `x/y`.
- Modo recursos (X): los seis recursos con nombre y cantidad/cap.
- Panel lateral: estado, descripción, producción/consumo, buffer, reserva y día de construcción.
- Minimapa con región explorada, módulos, cables y viewport.
- Menú de construcción por pestañas (Energía, Extracción, Soporte, Logística, Ciencia); categorías vacías ocultas, no disponibles en gris con “Investigar”. Recursos con iconos; cada módulo muestra coste con icono/cantidad, descripción y flujo produce/consume.
- Badges de modo/pausa y celda seleccionada; X cambia capa también en modo colocar.
- Consola de tecnología: una pantalla simple, sin pestañas vacías.
- Menú de pausa con Continuar/Créditos; créditos con scroll y easter egg.

## Planificado

- **Chatarra y reciclador:** ruinas alrededor del hábitat, demolición desde el día 0 con retorno parcial y reciclador que convierte chatarra en mineral. La chatarra es un recurso de red con cap propio.
- **Trampa de peces:** módulo barato sobre agua, conectado por cable; produce 1-2 comida por noche y se detiene si el agua se agota.
- **Batería:** el almacén deja de dar cap de energía; la batería pasa a ser el reservorio de energía.
- **Agua y radar:** depósito garantizado + depósitos RNG finitos; el radar encuentra todo y es la exploración permanente.
- **Bosques y cristales:** contenido base futuro; bosques renovables con brotes y cristales subterráneos finitos. Sus usos se definirán antes de implementarlos.
- **Costes multi-material:** construcciones y tecnologías podrán pedir más de un material; la obra recuerda lo pagado y los reembolsos se definen en [plan.md](plan.md).

## Backlog

- Mejoras Mk II, alimañas ambientales, tower defense, botín, inventario y variantes de muerte.
- Desgaste, eventos climáticos, radio y finales.
- Pulido de UI (9-slice, autotile, animaciones, overview) solo si el contenido lo pide.
- Chatarra/reciclador, trampa de peces, batería, agua RNG/radar y bosques/cristales están planificados en [plan.md](plan.md), no en este backlog.
