> **Nota:** brainstorm histórico del concepto original. Las ideas nuevas y las decisiones vigentes están en [plan-fase4.md](plan-fase4.md) (UI, tecnología, recursos y apagado), [plan-ui.md](plan-ui.md) (layout y assets) y [plan-fase5.md](plan-fase5.md) (alimañas, tower defense, botín, inventario y muerte).

User: estoy pensando en un juego basado en la terminal que permita vivir la experiencia "factorio" me gusta la idea de la gestion de la ambientacion "supervivencia en un planeta extaño" y la satisfaccion de ver los numeros crecer. para simplificarlo pensé el bloque que se van interconectando llevando materiales de un lugar a otro y transformandolos, la dificultad aqui no seria en como ubicarlos (el sistema me va armando el grafo) si no de la gestion de recursos, debo ir a cada modulo, supervisarlo, revisarlo, medir su productividad y capacidad, revisar las conexiones, administrar los recursos, la energia el agua, explorar para encontrar recursos distantes, etc... laslineas de trasnporte, los modulos de extraccion y las fabricas se van deteriorando, tener muchas implica revisar muchas cosas, empieza de grande a pequeño donde cada tecnologia o investigacion me desbloque cosas nuevas, sensores nuevos, herramientas nuevas, robots nuevos, yo superviso todo desde el panel de control donde undiagrama ascii me permite ver el esquema de mi fabrica, puedo ver analisis de producion, gasto, desgaste, riesgos, etc... con graficas de barras que hagan facil de visualizar los detalles. la interfaz la veo como el diagrama principal y una barra lateral, sirviendonos de inspiracion juegos clasicos como simcity y los tycoon, pero pensado para vivir en la terminal, donde nosotros somos el astronauta atrapado, que debecontrolar y hacer crecer todo usando maquinas robotizadas sin salir del modulo habitacional ya que la interperie es extremadamente peligrosa. debe tambien generar y almacenar alimentos. no hay amenaza de creaturas extraterrestres mas alla de pequeñas alimañas que puedan roer los cables, causar cortocirtuitos o comerse sus reservas. la otra inspiracion es el libro The Martian, pero quiero una historia nueva y unica. Necesito analizar los pros y los contras de esta idea, los huecos, los asustos a resolver y la viabilidad del proyecto.
AI: Es una idea **excelente y muy coherente**. Contextualizar un juego de terminal como la "consola de un astronauta atrapado en su módulo de mando" hace que las limitaciones del medio (la falta de gráficos 3D/2D complejos) se conviertan en su **mayor virtud narrativa y de inmersión**. Se siente natural interactuar con la terminal porque *eso es exactamente lo que haría el personaje*.

Recuerda a una mezcla entre *Factorio*, *Dwarf Fortress*, *Duskers*, *Subnautica* (en la gestión de supervivencia) y la novela *The Martian*.

A continuación, presento un análisis detallado de los **Pros, Contras, Huecos en el diseño, Asuntos a resolver y Viabilidad** del proyecto.

---

### 🟢 Pros (Puntos Fuertes)

1. **Inmersión Diegética Perfecta:** La interfaz *es* el juego. No hay disonancia entre la pantalla del jugador y lo que ve el personaje. Esto genera una atmósfera de soledad y tensión muy potente.
2. **Abstracción Logística (Grafo vs. Espacio):** Al eliminar la necesidad de construir una grilla visual 2D estricta tipo *Factorio* y pasar a un sistema de **grafos**, simplificas radicalmente la programación de la UI y el motor, permitiéndote enfocar la complejidad en las variables de simulación (eficiencia, temperatura, desgaste, flujo de datos).
3. **Escalabilidad del Desarrollo:** Trabajar en texto/ASCII permite iterar rápido. Puedes añadir 10 nuevos tipos de recursos o 5 tecnologías en cuestión de horas, sin tener que diseñar sprites, animaciones o modelos 3D.
4. **Nicho de Mercado Atractivo:** Existe un público muy fiel para los "TUI Games" (Text User Interface) y los juegos de gestión táctica/hardcore (fans de *Zachtronics*, *Cogmind*, *Aurora 4X*).
5. **Sensación de Logro "Tycoon":** Las gráficas de barras, los tableros que pasan de estar en "Rojo" a "Verde", y los registros de rendimiento (*logs*) son altamente adictivos cuando el jugador siente que ha "optimizado" el sistema.

---

### 🔴 Contras y Riesgos

1. **El Peligro de la "Tarea Doméstica" (Micro-gestión aburrida):** 
   * Si las máquinas se deterioran y el jugador debe ir manualmente a reparar la "Mina A", la "Mina B" y la "Mina C" haciendo scroll o escribiendo comandos repetitivos, el juego se vuelve un trabajo tedioso (*Whack-a-mole* o "jugar a apagar incendios constantes").
2. **Falta de Feedback Visual de "Dopamina":**
   * En *Factorio*, ver las cintas transportadoras mover miles de items visualmente es hipnótico. En texto, corres el riesgo de que todo se reduzca a "números cambiando en una tabla", lo cual puede perder el atractivo visual rápido si no se diseña la interfaz con suficiente dinamismo (ASCII animado, colores ANSI, parpadeos, etc.).
3. **Sobrecarga de Información (Cognitive Overload):**
   * Pasar de "pocos módulos" a "cientos de módulos" en formato texto puede saturar la pantalla. Si la interfaz no está extremadamente bien organizada, el jugador se sentirá abrumado y cerrado al sistema.

---

### 🕳️ Huecos de Diseño y Preguntas sin Resolver

1. **¿Cómo funciona la Exploración sin salir del módulo?**
   * Si no puedes salir, ¿cómo descubres nuevos yacimientos de hierro o agua subterránea?
   * *Solución sugerida:* Drones/Sondas de exploración que envías en un mapa de sectores, o radares espectrales que consumen mucha energía pero revelan el mapa poco a poco.
2. **¿Cómo se resuelven las distancias en un sistema de Grafos?**
   * Si el sistema arma el grafo automáticamente, ¿la distancia importa?
   * *Pregunta a resolver:* ¿Cuesta más energía/materiales conectar un nodo lejano? Si una tubería pasa por terreno hostil, ¿se desgasta más rápido?
3. **¿Cuál es la condición de Victoria o Fin de Juego (End Game)?**
   * En *The Martian*, el objetivo es ser rescatado. En *Factorio*, lanzar un cohete. ¿Aquí el jugador busca enviar una señal de auxilio, construir una nave para escapar, o transformar el planeta (Terraformación a escala de texto)?
4. **El Impacto de las Alimañas (Plagas):**
   * Dijiste que hay criaturas que roen cables. ¿Cómo interactúa el jugador con esto desde la terminal? ¿Ponemos trampa-robots, emitimos frecuencias de ultrasonido desde la terminal, o sellamos módulos?

---

### 🛠️ Asuntos Clave a Resolver (Mecánicas y Loop de Juego)

Para que el juego funcione, el ciclo principal de juego (*Core Loop*) debería ser así:

1. **Supervivencia Básica:** Mantener CO2 bajo, O2 alto, calor en el hábitat y suficiente comida (cultivos hidropónicos).
2. **Expansión Automatizada:** Colocar extractores -> Conectar a red eléctrica -> Generar recursos -> Construir fábricas de piezas.
3. **Mantenimiento y Diagnóstico:** Un módulo falla -> Mirar los gráficos de rendimiento -> Identificar la causa (¿falta energía?, ¿un cable fue roído?, ¿se desgastó por polvo?).
4. **Investigación y Automatización del Mantenimiento:**
   * *Fase temprana:* El jugador diagnostica y envía "Drones de reparación" manualmente.
   * *Fase tardía:* El jugador investiga algoritmos (o compra "Sub-Rutinas de IA") que reparan automáticamente según prioridades. **La automatización debe aplicarse también a la gestión, no solo a la producción.**

---

### 💻 Viabilidad Técnica y Tecnologías

El proyecto es **100% Viable** y puede ser desarrollado por un desarrollador independiente o un grupo pequeño en un tiempo razonable.

* **Lenguajes/Librerías recomendadas:**
  * **Python:** Usando **`Textual`** o **`Rich`**. *Textual* es una librería fantástica moderna para interfaces de terminal avanzadas (permite pestañas, botones, gráficas, barras laterales, ventanas divididas con diseño CSS-like).
  * **Rust:** Usando **`Ratatui`** (antiguo `tui-rs`). Es ultrarrápido, ideal si la simulación de miles de nodos en el grafo requiere mucho cálculo.
  * **C++ / C#:** Usando `ncurses` o frameworks similares.
* **Sonido:** Incluir efectos de sonido retro de terminal (tecleo, pitidos de alerta, zumbidos de estática) elevará el juego de "un proyecto académico" a "una experiencia inmersiva".

---

### 💡 Recomendaciones para llevarlo al siguiente nivel

1. **La Interfaz "HUD" del Astronauta:**
   * Divide la pantalla en 3 zonas:
     * **Izquierda (Barra lateral):** Estado vital del jugador (Hambre, Salud, O2 del hábitat), Recursos globales (Energía libre, Agua, Almacenamiento).
     * **Centro (Diagrama/Grafo ASCII):** El esquema visual de la red activa (puedes filtrar por Red Eléctrica, Red de Fluidos, Red de Datos).
     * **Derecha/Abajo (Telemetría y Consola de Comandos):** Gráficas ASCII (`📊 85% Prod`), logs del sistema (`[WARN] Caída de tensión en Sector C-3`), y panel de control.
2. **Transición de Escala:**
   * Empieza con el astronauta gestionando "1 Invernadero + 1 Panel Solar + 1 Batería".
   * Termina con el astronauta viendo agrupaciones gigantes de nodos (Macro-módulos), donde ya no gestiona cable por cable, sino "Sub-redes".
3. **Clima Dinámico:**
   * Tormentas de arena que tapan paneles solares (cae la energía), heladas nocturnas que congelan tuberías de agua si no hay calefactores encendidos. Esto le da emoción sin necesidad de monstruos atacando.

### Conclusión
Tienes una base **sólida, viable y muy original**. La clave para que sea divertido reside en **cómo evitas la monotonía de la reparación**: el jugador debe sentir la satisfacción de *programar su supervivencia* a través de la interfaz para que el sistema trabaje para él, permitiéndole ver los números crecer mientras el entorno hostil intenta destruirlo.

User: para evitr el overloa, pienso que se den avances tecnologicos que automaticen completamente los problemas de las etapas anteriores (se van sobreponiendo), asi cuando tenga trampas para alimañas ya no tengo que estar cazandolas o reemplazando cables, y luego con las trampas avanzadas ya no tengo que recoger los cadaveres y me puedo olvidar de las alimañas para preocuparme por otras cosas, luego tendre robots automaticos que reparan los modulos y asi puedo olvidarme de algunos modulos equipados con estos, pero esto trae problemas como la gestion energetica por lo que paso a preocuparme mas por la investigacion o mejora de las fuentes de energia, pero para eso tendre que explorar (drones, radares, en el futuro satelites), Quizas no lo hagamos 100% consola, puede ser grafica, pero que conserve la esencia de ser la interfaz desde donde el astronauta controle todo, me gusta python. las distancias en el grafo si afectan, pero lo unico que cambian es el color de la conexion, o el peso, al inspeccionar laconexion puedo ver sus detalles, conexiones mas largas son mas dificiles de reparar o mas propensas afallos,ademas de requerir mas material o materiales mas avanzados pueden requerir modulos intermedios como bombas o subestaciones. Las alimañas son solo un elemento narrativo, asi como el medio amiente produce desgastes o problemas, las alimañas producen problemas. el fin del juego puede tener dos posibles finales, alllegar a un estadio de Automatizacion completa, obtiene la medalla de planeta terraformado y una secuencia diciendo como la fabrica se expandio hasta dominar el planeta y luego de la muerte por causas naturales del astronauta la IA quedó como amo y señor del planeta. o el final de escape, donde ya sea por sus propios medios o mandando una señal de auxilio el astronauta sale del planeta, la señal de auxilio depende de la suerte y desbloquea una parte donde debera hablar con las navesque pasen y convencerlas de rescatarlo u ofrecerles recursos y asi (con la posibilidad de ser atacado y acabar con el final malo de ser destruido o secuestrado) (aqui quiero tomar inspiracion de ur quan masters) o salir porsus propios medios que es final estandar donde construye una nave y se va.
AI: ¡Tus nuevas ideas **resuelven exactamente los puntos débiles** que mencionamos anteriormente! La forma en que planteas la progresión y los finales le da al proyecto una personalidad única.

A continuación, hago un análisis de estas nuevas adiciones, los ajustes de diseño y cómo implementar esto en **Python**.

---

### 1. El Sistema de "Capas de Abstracción" (Solución al Overload)

El concepto de **abstracción progresiva** es brillante y es la clave del éxito en juegos como *Factorio* o *Satisfactory*:
* **Fase 1 (Manual/Micro):** Atrapas alimañas a mano, cambias cables rotos, mides el voltaje.
* **Fase 2 (Semiautomática):** Colocas trampas y sensores. La terminal te avisa exactamente dónde está el problema, ahorrándote tiempo de diagnóstico.
* **Fase 3 (Automatizada):** Trampas con triturador/biomasa (el cadáver se convierte en abono para el invernadero) + Drones de mantenimiento.
* **Fase 4 (Macro):** Te olvidas del módulo individual y gestionas **Redes** (Red Solar Norte, Red Hydro-Alfa). El juego cambia de "simulador de técnico" a "simulador de Ingeniero Jefe / IA".

> **Impacto de Diseño:** Esto elimina el aburrimiento. El jugador nunca siente que hace "lo mismo", porque los problemas viejos desaparecen automáticamente y son reemplazados por problemas de mayor escala (ej. *"Ya no me preocupan los cables roídos, pero me queda un 5% de Uranio y la tormenta de polvo bloqueará los paneles solares en 3 días"*).

---

### 2. Redes y Grafos: La Física de las Distancias

Hacer que la distancia afecte el **peso de la arista (edge weight)** en el grafo es visual y mecánicamente muy intuitivo:

* **Pérdida de Carga (Atenuación):** Si conectas un panel solar a 2 kilómetros de distancia:
  * La línea se vuelve de color **Amarillo/Naranja** (indica resistencia/pérdida).
  * Llega solo el 70% de la energía.
  * *Solución:* El jugador debe investigar e insertar un módulo intermedio: una **Subestación Transformadora** o una **Batería de Relevo**.
* **Punto Único de Fallo (Single Point of Failure):** Si una línea muy larga y cargada se rompe, toda la rama del grafo aguas abajo se apaga. Esto obliga al jugador a crear **redes redundantes** (anillos en lugar de árboles).

---

### 3. La Decisión Gráfica vs. Terminal (Con Python)

Si decides no usar una terminal de comandos pura de Linux/Windows, sino una **GUI que simule un Monitor CRT / Consola de Operaciones de Nave espacial**, abres un abanico de posibilidades estéticas increíbles (piensa en la estética de *Alien 1979*, *Fallout Pip-Boy* o *Duskers*).

En **Python**, tienes dos caminos principales para esto:

#### Opción A: GUI Basada en Texto Avanzada (`Textual` framework)
* **Ventajas:** Sigue corriendo en la terminal, pero parece una aplicación completa con ventanas, botones, gráficos de barras dinámicos y ratón.
* **Por qué usarlo:** Es nativo de terminal, ultra ligero, muy rápido de programar y se ve increíblemente retro-cyberpunk sin necesidad de dibujar sprites.

#### Opción B: GUI Gráfica Retro (`Pygame` o `Arcade` + Shaders CRT)
* **Ventajas:** Te da control absoluto de cada píxel. Puedes dibujar mapas de nodos con líneas brillantes, aplicar un efecto de pantalla curva CRT (con líneas de escaneo/scanlines), destellos de luz verdes/amarillos, y fuentes tipográficas vectoriales.
* **Por qué usarlo:** Puedes hacer gráficos de vectores dinámicos para los grafos (como los radares militares antiguos) que serían muy difíciles en texto puro.

---

### 4. Los Tres Finales y la Inspiración en *Ur-Quan Masters*

La inclusión de la radio y los contactos espaciales al estilo *Star Control / Ur-Quan Masters* es un giro genial para el final del juego.

```
                    ┌─────────────────────────────────────────┐
                    │      FASE FINAL DE SUPERVIVENCIA        │
                    └────────────────────┬────────────────────┘
                                         │
         ┌───────────────────────────────┼───────────────────────────────┐
         ▼                               ▼                               ▼
 ┌──────────────┐                ┌──────────────┐                ┌──────────────┐
 │ terraformar  │                │ CONSTRUCCIÓN │                │  SENAL DE    │
 │ (stay & ai)  │                │   DE NAVE    │                │   AUXILIO    │
 └───────┬──────┘                └───────┬──────┘                └───────┬──────┘
         │                               │                               │
  Auto-expansión                 Escape estándar                  Radio-Diplomacia
  infinita.                      requiere toneladas              estilo Star Control:
  La IA hereda                   de recursos raros.              - Mercaderes
  el planeta.                                                    - Piratas (Emboscada)
                                                                 - Salvadores alienígenas
```

* **El Final de la Señal de Auxilio (Radio-Diplomacia):**
  * Construyes una **Antena de Espacio Profundo**.
  * Empiezas a escanear frecuencias.
  * Aparece un cuadro de texto en tu pantalla: `"SEÑAL DETECTADA: Carguero de la Corporación Vextor"`.
  * Inicias un diálogo por texto. Tienes que convencerlos, negociar con tus recursos almacenados, o mentirles.
  * **Riesgo:** Responder mal a una nave desconocida puede atraer a piratas que envíen un pulso electromagnético (EMP) desde la órbita, destruyendo tus sistemas y provocando el "Bad Ending".

---

### 🕳️ Nuevos Huecos a Considerar

1. **Gestión del Tiempo del Jugador (Tiempo Real vs. Turnos):**
   * ¿El juego avanza en tiempo real (segundos/minutos) o avanza cuando el jugador ejecuta acciones o pasa de "Turno/Día"?
   * *Recomendación:* Tiempo real pausable. Da la sensación de urgencia cuando hay una falla crítica en el reactor mientras intentas responder a una llamada de radio.
2. **El Recurso "Espacio en el Módulo Habitacional":**
   * Como no sales del módulo, el hábitat tiene espacio limitado para servidores de investigación, consolas de radio o sistemas de soporte vital. Deberás decidir qué instalar dentro de tu refugio.

---

### 📋 Veredicto y Siguiente Paso Recomendado

La idea está **lista para prototipar**. Tienes una narrativa fuerte, mecánicas claras que resuelven los problemas de diseño y un alcance técnico muy abordable en **Python**.

**Prototipo Mínimo Viable (MVP) para empezar a programar:**
1. Crear una estructura de datos en Python para el **Grafo** (usando la librería `NetworkX`).
2. Crear 3 tipos de nodos: *Generador Solar*, *Batería*, *Invernadero*.
3. Simular el ciclo de Energía y Comida en un bucle simple (`while True:`).
4. Diseñar la UI visual con `Textual` o `Pygame` para mostrar el grafo conectado con líneas de colores según la eficiencia.

User: que tan dificil es programar un juego para PortMaster para la R36s?
AI: Programar este juego para la **R36S a través de PortMaster** es de una dificultad **FÁCIL a MEDIA (3/10 a 5/10)**, y la buena noticia es que **la R36S es la consola perfecta para este concepto**.

La R36S usa el chip **RK3326** con 1 GB de RAM y una pantalla de 3.5" con resolución **640x480**. Para un juego de gestión en 2D/Python, este hardware va sobrado de potencia.

Aquí tienes el análisis de cómo adaptarlo, los retos técnicos y el flujo de trabajo:

---

### 🟢 ¿Por qué es una gran idea?

1. **La Pantalla 640x480 (4:3):** Es la resolución ideal para simular un monitor retro de PC de los años 80/90. El texto se verá nítido y la interfaz de consola/gráficos lucirá increíblemente bien.
2. **Soporte Nativo de Python en PortMaster:** PortMaster tiene ejecutable y entornos de **Python 3 y Pygame** ya listos (runtimes). No tienes que compilar código complejo en C++.
3. **Factor "Nostalgia/Portabilidad":** Jugar a un juego de gestión profunda estilo *The Martian* en una consola portátil parece una experiencia de ciencia ficción retro genial.

---

### ⚠️ Los 3 Grandes Retos Técnicos

El hardware de la R36S impone tres limitaciones que debes solucionar en el diseño:

#### 1. Sin Teclado (El mayor reto)
La R36S solo tiene cruceta (D-Pad), dos joysticks análogos, botones ABXY, Select/Start y gatillos. No hay teclado ni pantalla táctil.
* **Solución A (Estilo Ratón):** Usar el joystick analógico izquierdo para mover un cursor de ratón en pantalla y el botón `A` como clic. Pygame maneja esto con 3 líneas de código.
* **Solución B (Navegación por Nodos/Menu):** Moverte por el grafo usando la cruceta (Arriba/Abajo para cambiar de módulo, Izquierda/Derecha para ajustar valores). Esto es más cómodo para el jugador.

#### 2. Tamaño del Texto y Legibilidad
Una pantalla de 3.5 pulgadas es pequeña. Si usas fuentes tipográficas de terminal demasiado pequeñas o metas demasiado texto denso, el jugador se quemará los ojos.
* **Solución:** Diseñar la interfaz específicamente para 640x480 usando fuentes "Pixel Art" o "Monospaced" grandes (ej. *VT323* o *Fira Code* en tamaño 14-18pt).

#### 3. Olvídate de la Terminal Real (Usa Pygame)
Intentar ejecutar el juego en la terminal nativa de Linux (ArkOS) dentro de la consola es una pesadilla para mapear controles.
* **Solución:** Crea el juego en **Python usando `Pygame` (o `Pygame-CE`)**. Dibuja la "Terminal" dentro de la ventana de Pygame. Así tienes control total del renderizado, colores, botones de la consola y FPS.

---

### 🛠️ ¿Cómo funciona la arquitectura en PortMaster?

PortMaster es súper simple. Solo necesita una estructura de carpetas como esta dentro de tu SD:

```text
roms/
 └── ports/
      ├── MiJuegoEspacial.sh   <-- Script de arranque en Bash
      └── mijuego/             <-- Tu carpeta con el juego
           ├── main.py         <-- Tu código Python
           ├── assets/         <-- Fuentes, sonidos, imágenes
           └── run.sh          <-- Llama al entorno Python de PortMaster
```

#### El Script de Lanzamiento (`MiJuegoEspacial.sh`)
PortMaster incluye un programa llamado `gptokeyb` (Gamepad to Keyboard). Si no quieres programar el soporte para mando en Python, `gptokeyb` convierte los botones de la R36S en teclas de teclado automáticamente:

* Presionar `Cruceta Arriba` en la R36S -> Envía la tecla `Flecha Arriba` al juego.
* Presionar Botón `A` -> Envía la tecla `Enter` o `Espacio`.

---

### 🚀 Flujo de Trabajo Recomendado

1. **Desarrolla el 95% en tu PC:**
   * Programa todo el juego en tu ordenador usando Python y Pygame a una resolución fija de **640x480**.
   * Limita la interacción al teclado (Flechas, Enter, TAB) o al ratón.
2. **Prueba los Controles:**
   * Conecta un mando de Xbox/PlayStation a tu PC para asegurarte de que la interfaz se navega bien sin usar el ratón si decides no usar cursor.
3. **Empaqueta para PortMaster:**
   * Copia tu carpeta de juego a la R36S.
   * Usa el runtime de Python que PortMaster provee por defecto.
4. **¡A jugar!**

### Conclusión sobre la Dificultad
Si sabes escribir código en Python básico-intermedio y usar `Pygame`, **hacerlo funcionar en la R36S no te tomará más de una tarde de trabajo de configuración**. 

Lo verdaderamente complejo será **el diseño de la interfaz** (hacer que se vea bonita a 640x480 y se controle bien con mandos), pero como motor y despliegue, es un proyecto 100% viable y muy gratificante.

User: necesito ideas para como nombrar el juego
AI: Para elegir el nombre ideal, es buena idea definir qué aspecto del juego quieres destacar más: **la interfaz técnica (el terminal), la narrativa de aislamiento (el astronauta atrapado) o la mecánica de redes y automatización**.

Como el juego correrá en una pantalla retro de 640x480 (como la R36S) y busca esa estética *cyberpunk/sci-fi vintage*, los nombres estilo **sistema operativo, comando o clave técnica** quedan espectaculares.

Aquí tienes varias opciones divididas por la "vibra" que transmiten:

---

### 💻 Opción 1: Nombres Estilo "Sistema Operativo / Comando"
*(Hacen que el jugador sienta que no está ejecutando un "juego", sino un programa de control real).*

1. **`HAB_OS: Protocol`** (O simplemente `HAB_OS`). Corto, potente y suena exactamente a lo que es: el sistema operativo de tu hábitat.
2. **`EXO_GRID`** o **`EXO_NODE`**. Refleja perfectamente la mecánica de grafos/nodos y el entorno extraterrestre.
3. **`SYS_SOLITUDE`**. Mezcla lo técnico (`SYS`) con el tema narrativo del aislamiento (`SOLITUDE`).
4. **`TELEMETRY`**. Elegante, técnico y va directo al grano: gestionar datos a la distancia.
5. **`SUBROUTINE`**. Hace referencia a cómo vas automatizando tareas y al destino final donde la IA se queda a cargo.

---

### 🛰️ Opción 2: Nombres Narrativos / Tensión y Aislamiento
*(Ponen el foco en la historia del astronauta atrapado que no puede salir al exterior).*

1. **`Behind the Glass`** *(Detrás del cristal)*. Muy poético. Recuerda a la barrera entre la seguridad del módulo y el planeta peligroso.
2. **`Hermit Protocol`** *(Protocolo Ermitaño)*. Encaja muy bien con la idea de controlar todo sin pisar jamás el exterior.
3. **`Don't Open the Hatch`** *(No abras la escotilla)*. Da una sensación inmediata de peligro y supervivencia.
4. **`Dust & Circuits`** *(Polvo y Circuitos)*. Resume la lucha contra el planeta (polvo/desgaste) usando tus máquinas (circuitos).
5. **`The Indoor Engineer`** *(El Ingeniero de Interiores)*. Un toque de humor negro e irónico sobre tu situación.

---

### ⚙️ Opción 3: Nombres Directos / Tipo "Tycoon / Factorio"
*(Atraen al jugador al que le gustan los números, la logística y ver crecer la fábrica).*

1. **`Exo-Factory: Terminal`**
2. **`Node-Bound`** (Un juego de palabras entre estar "atado a los nodos" y "atado al módulo").
3. **`Automata Prime`**
4. **`Signal & Rust`** *(Señal y Óxido)*. Excelente para el loop de radio + deterioro de maquinaria.

---

### 🇪🇸 Opción 4: Nombres en Español (Si el juego es 100% en español)
*(A veces un nombre en español le da una personalidad muy única y de "juego de autor").*

1. **`Módulo-7`** (o cualquier número que suene a misión espacial).
2. **`Aislamiento: Red Cero`**
3. **`Sin Salida`** / **`Fuera de Servicio`**
4. **`Tele-Control`**

---

### 🏆 Mis 3 Favoritos para la R36S (Pantalla 640x480):

Si tuviera que elegir los que mejor se ven en la portada de PortMaster y en la pantalla de título retro:

1. 🥇 **`EXO_GRID`** (Fácil de recordar, suena pro y profesional).
2. 🥈 **`HAB_OS`** (Minimalista. En la pantalla de inicio puedes poner "HAB_OS v1.0 - Press Start").
3. 🥉 **`Behind the Glass`** (El mejor si quieres que la historia y la atmósfera de *The Martian* pesen más).

**Un consejo visual:** Elige un nombre que se pueda escribir en tipografía de matriz de puntos (Pixel Art) o letra verde fosforescente de fósforo verde (monospaced). ¡Quedará increíble en la R36S!

