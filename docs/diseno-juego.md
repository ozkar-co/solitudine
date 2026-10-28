# Diseño del juego

> Este documento describe el juego. El roadmap y los números concretos viven en [plan.md](plan.md); el código en [arquitectura.md](arquitectura.md).

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
- Módulos: hábitat, solar, radar, extractor, invernadero, mina, fabricador, almacén y lámpara.
- Todo se conecta por cables desde el hábitat. Sin conexión, el módulo queda offline.
- **R1** apaga/enciende el módulo seleccionado (excepto el hábitat).
- Un módulo apagado no produce, no consume energía, no aporta visión, no suma capacidad de almacén y no emite luz.

## Recursos y supervivencia

- Recursos: O₂, energía, agua, comida, mineral y componentes.
- O₂, agua y comida son letales al llegar a cero; la energía es una restricción, no una muerte directa.
- Los depósitos de agua/mineral son finitos.
- La matriz de fuentes/usos y los próximos cambios están en [plan.md](plan.md).

## Red y logística

- Los módulos producen a buffers locales; la red tiene capacidad limitada.
- El almacén amplía la capacidad de la red.
- La energía se reparte proporcionalmente si falta; un módulo sin energía produce menos.
- Los productores se detienen al llenar su buffer o la red.

## Luz y día/noche

- La noche dibuja un dithering sobre el terreno; la luz lo reduce.
- El hábitat ilumina desde el inicio; la lámpara amplía la zona iluminada.
- La lámpara consume energía solo de noche, proporcional a la oscuridad (máx. 4 E/día).
- La luz no cambia producción ni consumo.

## Exploración e investigación

- Solo el radar explora de forma permanente; el resto da visión local.
- La investigación desbloquea módulos; el próximo slice es laboratorio + 2 tecnologías.
- Exploración avanzada, alimañas, botín y combate están en backlog.

## Controles

| Acción | PC (`--dev`) | Mando |
|--------|--------------|-------|
| Mover cursor | Flechas / WASD | L-stick / DPAD |
| Mover cámara | Arrastrar con botón medio / right stick | R-stick |
| Seleccionar tile | A / Enter | A |
| Construir | Y | Y |
| Cambiar capa | X | X |
| Cancelar | B / Esc | B |
| Zoom | L1/L2 (teclas Q/E o [/]) | L1/L2 |
| Apagar/encender | R1 | R1 |
| Minimapa | R2 | R2 |
| Pausa | START | START |
| Salir | SELECT+START | SELECT+START |

## UI

- 640×480, grilla de 16 px, fuente VT323 y sprites propios.
- Barra superior: O₂, agua, comida y energía.
- Panel lateral: tile, estado, flujos, buffer y acciones.
- Minimapa con región explorada, módulos, cables y viewport.
- Consola de tecnología: una pantalla simple, sin pestañas vacías.

## Backlog

- Alimañas ambientales (roer cables) primero; tower defense más adelante.
- Inventario genérico, botín y variantes de muerte.
- Desgaste, eventos climáticos, radio y finales.
- Reciclaje, batería y más tecnologías.
- Pulido de UI (scroll, autotile, overview) solo si el contenido lo pide.
