# Solitudine — Documento de diseño

> Borrador vivo para la etapa inicial. Edita libremente; esto es la fuente de verdad antes de programar mecánicas nuevas.

---

## 1. Visión en una frase

Supervivencia y gestión industrial en un planeta hostil: eres un astronauta atrapado en el hábitat, controlas robots y módulos remotos desde una consola retro, y ves crecer tu colonia mientras el entorno intenta desgastarlo todo.

**Inspiraciones:** *The Martian*, *Factorio*, *SimCity* / tycoons clásicos, *Ur-Quan Masters* (rama de rescate por radio).

---

## 2. Cambio de dirección: grafo → mapa

### Antes (ideas iniciales)

- Red abstracta en **grafo**: el sistema conectaba nodos; la dificultad era gestionar flujos, no ubicar cosas.
- UI centrada en **diagrama ASCII** de la red.

### Ahora (decisión actual)

- **Mapa geográfico 2D** (Pygame, 640×480): los módulos tienen posición en el terreno.
- **El terreno importa:** distancia, biomas, obstáculos, clima local, desgaste de líneas que cruzan zonas hostiles.
- **Desaparece el grafo como interfaz principal.** Las conexiones existen, pero se entienden como tuberías/cables/trenes *sobre el mapa*, no como nodos abstractos.
- La consola del astronauta sigue siendo diegética: no sales del hábitat; el mapa es la vista de telemetría / drones / sensores.

### Implicaciones del mapa

| Aspecto | Con grafo | Con mapa |
|---------|-----------|----------|
| Colocar módulos | Automático o irrelevante | Decisión del jugador (¿o asistida?) |
| Distancia | Peso/color de arista | Geometría real + coste de tendido |
| Exploración | Sondas en sectores | Niebla de guerra, tiles, rutas |
| Complejidad UI | Tablas + diagrama | Vista mapa + panel lateral |
| Arte | ASCII / texto | Tiles, iconos, líneas (KISS en 640×480) |
| Rendimiento R36S | Muy ligero | Cuidado con escala; pocas entidades al inicio |

---

## 3. Lo que se mantiene

- **Fantasía:** astronauta solo en el módulo; exterior letal.
- **Loop tycoon:** números que suben, optimización, satisfacción de ver sistemas en verde.
- **Capas de automatización:** cada tecnología **elimina** micro-gestión vieja y abre problemas de mayor escala (trampas → robots → macro-redes).
- **Desgaste y mantenimiento:** módulos y líneas se deterioran; alimañas y clima como presión ambiental, no como combate.
- **Recursos:** energía, agua, O₂, comida, materiales, almacenamiento.
- **Investigación** desbloquea sensores, herramientas, robots, satélites.
- **Finales múltiples:** escape (nave propia / señal de auxilio estilo UQM), terraformación + legado IA, mal final posible.
- **Stack:** Python + Pygame, PortMaster R36S, input directo (`LJOY_*`, `DPAD_*`, etc.).

---

## 4. Lo que hay que re-pensar por el mapa

- [x] **¿El jugador elige dónde construir** cada módulo o solo elige *qué* construir y el sistema sugiere sitio?
Creoque la opcion aqui es que el jugado elija donde construir, ademas debe conectar el modulo con la conexion correcta (tuberia,cables,etc) algunas conexiones pueden ir juntas por el mismo tile (para mantener mas ordenados las conexiones) algunas no son compatibles, el riego es que una tuberia dañada corta toda la conexion
- [x] **Escala del mapa:** ¿un sector pequeño al inicio que crece, o mapa grande con niebla?
el mapa será un mapa grande, como una cuadricula, emprecemos con 1024x1024 pero quizas cambie, ademas esta en negro lo no explorado pero hay niebla sobre lo que no tiene vigilancia constante. y la camara no se puede alejar si no hasta un rectangulo que envuelve lo ya explorado (Con un margen) asi no se pierde el jugador en un mapa inmenso.
- [x] **Conexiones:** ¿el jugador traza rutas (como tuberías), ¿auto-pathfinding con coste, o ambos?
el jugador debe trazar las rutas la va dibujando y el sistema detecta si debe poner curvas y asi, si la conexion entra en un modulo pregunta si conectar y da el coste, esto queda como plano, el robot builder lo debe construir y eso se ve como tiempo que se demora la construccion (no se ve el robot, el mapa sigue siendo esquematico) el numero de builders determina la cantidad de construcciones en paralelo y el tiempo que se demora cada construccion enfinalizarse.
- [x] **Cámara:** scroll con `LJOY`/cruceta, zoom necesario o tile size fijo para 640×480.
L1 y L2 hace zoom in y zoom out y RJOY mueve el mapa, LJOY sera igual que la cruceta y serviran para ubicar los elementos a construir, o para seleccionar en el mapa y asi.
- [x] **Representación:** tiles cuadrados, hex, iconos sobre fondo minimalista.
me gusta la grid hexagonal pero creo que en este caso es mejor la cuadrada, para tener modulos de distinto tamaño, puntos de conexion y ordenar las conexiones y todo eso.
- [x] **Colisiones:** ¿módulos ocupan espacio exclusivo? ¿líneas pueden compartir zanja?
el espacio de los modulos es exclusivo, las conexiones si pueden compartir una via (o lo harán con la tecnologia de pipes multicanal y cosas asi) y no se pueden cruzar hasta que se desallollen las tuberias subterraneas que pueden cubrir saltos bajos el terreno.

---

## 5. Estado técnico actual (implementado)

| Fase | Hecho |
|------|-------|
| 0 | Depurador de input; mando R36S sin gptokeyb; nombres semánticos en `gamepad.py` |
| — | Runtime pygame-ce, deploy PortMaster, modo dev con teclado |
| 1 | Mapa 1024², cámara, cursor, panel, capas terreno/agua/recursos |
| 2a | Simulación: día 48 s, reservas hábitat (O₂, E, agua, comida), consumo horario |
| 2b | Construcción: componentes, cable manual, panel solar, radar; red desde hábitat |

**Input estándar del juego:** `A`, `B`, `X`, `Y`, `L1`–`R2`, `SELECT`, `START`, `FN`, `DPAD_*`, `LJOY_*`, `RJOY_*`.

**Controles construcción:** `B` menú (pausa) → elegir → `A` colocar → trazar cable tile a tile con `A`.

---

## 6. Propuesta de interfaz (640×480)

```
┌─────────────────────────────────────────────┐
│ [barra estado: O2, energía, alertas]        │
├──────────────────┬──────────────────────────┤
│                  │  Panel lateral           │
│   MAPA           │  · módulo seleccionado   │
│   (scroll)       │  · producción / desgaste │
│   módulos        │  · acciones (A=confirm)  │
│   líneas         │  · log reciente          │
│   terreno        │                          │
├──────────────────┴──────────────────────────┤
│ [ayuda contextual / modo actual]            │
└─────────────────────────────────────────────┘
```

**Controles candidatos** *(marca lo que prefieras)*:

- [x] `LJOY` y cruceta: mover cursor o cámara ( si llega al borde mueve la camara)
- [x] `RJOY`: mover cámara
- [x] `A`: seleccionar / confirmar
- [x] `B`: cancelar / menú atrás
- [x] `X`: cambio de capa de mapa (recursos/agua/mapa) 
- [x] `Y`: quick repair/quick action
- [x] `L1`/`L2`: mapa zoom in y zoom out

---

## 7. Core loop (borrador)

1. **Revisar** mapa y alertas (algo en rojo).
2. **Diagnosticar** módulo o tramo (panel lateral, gráficas simples).
3. **Actuar:** reparar, enviar drone, cambiar prioridad, investigar, tender línea, construir.
4. **Expandir** cuando la red estable lo permita.
5. **Automatizar** vía investigación para no repetir pasos 1–3 en esa categoría.

*Tiempo:* ¿real pausable, ticks por turno, o días con botón “avanzar”? → el tiempo se puede pausar, se pausa automaticamente mientras se dan las ordenes, se diseña lo que se va a construir y eso, el tiempo no se va a poder adelantar (excepto en modo dev para debug) transcurre al ritmo que debe transcurrir balancearemos los tiempos de espera y de construccion para que no sean aburridos.

---

## 8. Sistemas del juego

### 8.1 Mapa y terreno

- [x] Tamaño inicial (ej. 32×32 tiles visibles, mundo más grande).
el area inicial puede ser un circulo de 16 tiles de radio al rededor del modulo habitacional, luego se ira expandiendo, cada modulo conectado y funcional da un circulo de 4 de radio de vision desde cada uno de sus tiles (los modulos pueden ser grandes y tener distintas formas) dos modulos contiguos se asumen conectados y comparten recursos.
- [x] Tipos de tile: roca, polvo, hielo, cráter, cueva, *slot* construible…
inicialmente suelo,agua,roca. solo se puede construir sobre el suelo, un modo de escaneo de recursos permite identificar zonas de recursos de distinta densidad bajo la superficie, un modulo adecuado sobre esos tiles puede extraer el recurso.
- [x] Propiedades por tile: coste tendido, desgaste extra, bloqueo, bonus recurso.
el coste será dado solo por la distancia, el clima seran eventos aleatorios que cubriran zonas donde los tiles se veran afectados, entonces lo que tienen son propiedades transitivas como polvo acumulado, humedad acumulada, exposicion al acido, tiempo desde el ultimo mantenimiento/limpieza, suciedad, antiguedad, etc... asi como la cantidad de recursos presentes.
- [x] Clima por zona o global: tormenta de polvo, frío nocturno.
habran eventos por zona, que serán como nubes, mas concentrados en el centro y mas difusos a los bordes, la funcion para crear estas nubes debe ser la misma para crear las zonas de recursos durante la generacion del mundo (DRY) ya que se comportan igual, mas concentrados al centro, difusos a los bordes, de distintas formas y tamaños y que cubren todo el mapa. otros eventos seran globales como heladas, temporadas de intenso calor, terremotos, etc...

### 8.2 Módulos

- [x] Lista mínima viable (MVP): hábitat, panel solar, batería, invernadero, extractor, almacén.
para una version inicial esos que mencionas son practicamente suficientes, quizas añadir la torre vigia (o radar o antena) que da una vision de radio 24 y servirá no solo para explorar si no para mantener la visibilidad sin la sombra del mapa.
- [x] ¿Módulos pre-colocados al inicio o construyes el primero?
el unico modulo precolocado es el habitat en el cento del mundo, tiene recusos acumulados para unos cuantos dias, mientras el jugador va aprendiendo a recolectar los demas recursos.
- [x] Radio de influencia o solo conexión explícita por línea.
los modulos contiguos se asumen conectado, pero de resto debe haber conexion explicita, lo que no esté conectado al habitat no es controlable ni legible su estado (hasta que se desarrolle la tecnologia de conmunicacion inalambrica)
- [x] Estados: ok / degradado / offline. ok todo funciona hasta cierto nivel de daño, mientras este dañado pero no del todo se muesta degradado, el simbolo de alerta funciona como un semaforo, un circulo verde es ok, un triangulo amarillo significa que no esta funcionando al 100% y necesita reparacion mantenimiento, un cuadrado rojo es que esta demasiado dañado para funcionar o que esta desconectado o que algo impide que funcione.

### 8.3 Conexiones (sustituyen al grafo abstracto)

- [x] Tipos: cable eléctrico, tubería agua, cinta/bot logistic (¿cuáles en MVP?).
en el mvp tendremos solo conexion electrica (se asume comunicacion sobre esta misma), transportadora (para compartir recursos no liquidos) y tuberia general (para cualquier fluido, inicialmente el unico fluido sera agua)
- [x] Reglas: distancia máxima sin repetidor, bombas, subestaciones.
por ahora la distancia maxima sera 64 tiles, para cualquier tipo de conexion
- [x] Visual: color por carga/eficiencia/desgaste (como el color de arista del diseño viejo).
las conexiones tendran colores dependiendo del tipo de conexion y en caso de presentar una falla o estar demasiado desgastado aparecera un simbolo de alerta sobre el tile problematico, lo mismo los modulos.

### 8.4 Recursos y simulación

- [x] Tick de simulación: cada N segundos / cada día.
vamos por dias, un dia cada 48 segundos
- [x] Recursos globales vs por módulo.
las redes de distribucion comparten recursos instantaneamente, cada modulo puede almacenar hasta 10 unidades de lo que producen (esto determina el total de la red, pero tambien lo que pueden acumular si se desconectan) y los almacenes añaden capacidad a red.
- [x] ¿Colapso si sobre-produces sin almacén?
No, simplemente se detiene la produccion de los modulos que lleguen a su tope.

### 8.5 Supervivencia del astronauta

- [x] ¿Stats del astronauta (hambre, estrés) o solo del hábitat?
se tiene un estimado de consumo de alimento y agua, diario si las reservas del habitat bajan de eso se empieza a producir malestar en el astronauta, y ese malestar si afectará a variables propias del astronauta. 
- [x] Comida: invernadero obligatorio en early game.
la bomba de agua (modulo de extraccion cerca de agua o agua subterranea) y el invernadero seran los primeros modulos que construirá para garantizar la supervivencia y posiblemente luego de eso deje de ser una preocupacion la comida y el agua hasta que algo falle.

### 8.6 Presión ambiental

- [x] Desgaste base por clima, general de todo el mapa y dependera del tipo de mapa, por ahora solo hay uno y el desgaste es fijo por tiempo.
- [x] Eventos Climaticos: Se producen daños o acumulacion de suciedad, incremento del desgaste por eventos aleatorios en tiles especificos.
- [x] Alimañas: eventos en tramos/módulos; progresión trampas → automático.
- [x] Sin combate directo.

### 8.7 Exploración

- [x] Niebla de guerra.
Totalmente oscuro lo no explorado, con sombra lo inactivo, el modulo tiene un radar que va revelando casillas no exploradas en espiral para lentamenente ir agrandando de forma pasiva el mapa.
- [x] Drones/sondas/radar consumen energía y revelan tiles + yacimientos.
en la version inicial solo radares que muestran una zona y ya.
- [x] ¿Recursos solo en tiles descubiertos?
si, solo tiles explorados pueden mostrar los recursos que tienen, en la version inicial solo hay agua y carbon, a medida que se añadan recursos pueden requerir sondas especializadas para ver los niveles.

### 8.8 Investigación

- [x] Árbol lineal vs ramas.
el arbol puede tener ramas, el juegador decide que linea es la mas atractiva o la mas util en el estado particular del juego, ademas el RNG puede llevarlo a querer especializarse por la clase de recursos disponibles en el mapa, etc...
- [x] Categorías: sensores, automatización, energía, logística, comunicacion.

### 8.9 Finales

| Final | Condición (borrador) |
|-------|----------------------|
| Escape (nave) | Construir lanzadera con recursos tardíos |
| Escape (radio/UQM) | Antena, señales, diálogos, negociación, riesgo |
| Terraformación / IA | Automatización total; epílogo |
| Malo | EMP / secuestro / colapso hábitat |

- [x] ¿Un solo final por partida o ramas excluyentes?
si tendremos un solo final por partida, sea bueno o malo, da un informe final y se cierra.

---

## 9. Progresión por capas (recordatorio)

| Era | Jugador hace | Automatización desbloqueada |
|-----|--------------|-----------------------------|
| Early | Reparar cables, revisar invernadero a mano | — |
| Mid | Trampas, sensores, alertas precisas | Alimañas, diagnóstico |
| Late | Drones mantenimiento, macro-redes | Reparación rutinaria |
| End | Radio / nave / terraformación | Gestión por IA |

---

## 10. Preguntas abiertas (resolver antes de fase 1 de juego)

### Mapa y construcción

1. ¿Construcción libre en tiles válidos o solo en “slots” predefinidos?
la construccion sera libre en los tiles vacios.
2. ¿Rotación de módulos?
los modulos si se podran rotar, pero en el futuro, por ahora en el MVP todos los modulos ocupan un solo tile asi que no tiene sentido.
3. ¿Demoler / recuperar materiales?
demoler produce chatarra que puede ser almacenada para extraer luego recursos o limpiada para poder construir en el tile deshaciendose de los recursos.

### Logística

4. ¿Un solo tipo de “línea” al inicio o tres desde el MVP?
en el mvp un solo tipo de linea, hay conexion se asume que estan conectados y ya, con eso comparten energia, recusrsos, etc...
5. ¿Transporte automático una vez conectado o hay que “programar” rutas?
el transporte es automatico, mientras esten conectados en la misma red logistica comparten recursos, como inicialmente todo estara conectado al modulo habitat, solo hay una red logistica, pero esta logica permitirá que luego cosas funcionen independientemente, con comunicacion remota, aisladas (si hay conexion de comunicacion pero no de transporte) o que almacenen recursos por si solas y esos recursos no se pierdan.

### Ritmo

6. ¿Tiempo real pausable, turnos, o días discretos?
el tiempo se pausa mientras se planifica una construccion y puede pausarse el juego general, pero de resto va andando solo y se contabilizan los dias de 48 segundos (dos segundos por hora)
7. ¿Eventos scripted (tormenta día 5) o solo sistemas emergentes?
inicialmente los eventos estan definidos (scripted) pero luego se añadiran eventos aleatorios asociados al RNG del juego.

### Narrativa

8. ¿Nombre del planeta / misión / astronauta?
Aun no he definido el nombre del planeta, puede se un codigo NEP-325 o algo asi (Not Explored Planet, o UP: Unknown planet) es mas el nombre del planeta será la semilla del generador aleatorio, asi la combinacion de 3 letras y 3 numero produce los mismos planetas. el astronauta lleva el nombre del jugador, inicialmente Oz (en el mvp no es configurable aun, asi como la semilla es fija y no configurable en el mvp) 
9. ¿Logs de texto diegéticos (correos, informes) o solo UI técnica?
LA UI tecnica, el astronauta controla elsistema y esta pendiente y ya.
10. ¿Idioma del juego: ES, EN, ambos?
Inicialmente en español, pero de una vez creemos el soporte multilingue haciendo que todos los textos esten paramtrizados y archivos para cada idioma.

### Alcance MVP (primera versión jugable)

11. ¿Cuántos tipos de módulo en v1? ya se describio anteriormente.
12. ¿Un bioma o dos? inicialmente un solo bioma.
13. ¿Ganar/perder en MVP o solo sandbox de supervivencia? en el mvp solo supervivencia sandbox.

---

## 11. Riesgos a vigilar

- **Micro-gestión infinita** si el mapa multiplica objetos sin automatización.
- **UI ilegible** en 3.5" si hay demasiados tiles/iconos.
- **Scope creep** del mapa (pathfinding, zoom, edición) vs KISS.
- **Doble complejidad** terreno + simulación de recursos desde el día 1.

---

## 12. Roadmap de diseño sugerido (no código aún)

1. Responder sección 10 (marcar checkboxes arriba).
2. Boceto en papel del mapa MVP: hábitat + 3 módulos + 2 recursos.
3. Definir **un** ciclo día/noche o tick de simulación.
4. Lista cerrada de módulos y conexiones para v0.1.
5. Wireframe ASCII o mock 640×480 de la UI mapa + panel.
6. Entonces: fase 1 código = mapa estático + selección + panel vacío.

---

## 13. Referencias en el repo

- Brainstorm original y análisis: [ideas.md](ideas.md)
- Input: `src/gamepad.py`
- Código fase 0: `src/main.py`

---

## 14. Notas libres

Pienso que la partida guardada se puede llevar en SQLite y asi cada partida es un archivo db independiente.

---

## 15. Fase 2 — decisiones de construcción (cerradas)

### Materiales

- [x] Un solo tipo al inicio: **Componentes** (reserva inicial 30 en el hábitat).
- [ ] Futuro: subprocesos (metales → componentes, tipos especializados).

### Construcciones MVP

| Pieza | Coste | Tiempo | Notas |
|-------|-------|--------|-------|
| Cable | 1 / tile | Instantáneo | Trazado manual, solo suelo despejado |
| Panel solar | 8 | 1 día | +4 E/día si en línea |
| Radar | 12 | 1.5 días | −1 E/h; visión clara 16, neblina 24 |

### Red y estados

- [x] Red = hábitat + cables + módulos contiguos (BFS ortogonal).
- [x] Construcción requiere **componentes + suelo despejado**; avanza solo si hay cable a la red.
- [x] Módulo terminado sin cable: **Desconectado** (inactivo).
- [x] Visión fusionada por fuente (unión): hábitat 16+2 sombra, cable 1+1, solar 4, radar 16+24.

### Radar y subsuelo

- [x] Radio 16: terreno claro + **depósitos visibles** en capa Recursos.
- [x] Radio 17–24: neblina (explorado pero difuso).
- [x] Hábitat y otros módulos no revelan subsuelo en capa Recursos.
- [x] Depósitos generados: agua y carbono bajo suelo.


