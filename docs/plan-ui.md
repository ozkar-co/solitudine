# Plan de UI — base estable y assets pixel

> **Decisión vigente:** 2026-10-28. La UI se adelanta a las fases 4 y 5 para fijar layout, assets y contratos antes de añadir sistemas.
> Objetivo: una UI que no haya que rediseñar cuando lleguen apagado, tecnología, inventario, alimañas y muerte.

---

## 1. Diagnóstico actual

- Resolución lógica 640×480, barras de 32/22 px y panel de 168 px. El mapa mide 472×426.
- Todo el mapa se dibuja con `pygame.draw.rect`: no hay sprites ni assets.
- Zoom continuo de 6 a 40 px/tile; por defecto ~15,5 px/tile. Un zoom no entero impide un pixel art nítido.
- La barra superior muestra Cmp/E/O₂ y omite agua/comida.
- El panel lateral dibuja líneas fijas; no hay scroll ni componentes reutilizables.
- Modales y menús son listas de texto centradas; no hay estados visuales para apagado, daño, bloqueo o amenaza.
- No existe capa de estado de UI: el input muta `sim`/`world` directamente y cada pantalla lee campos sueltos.
- No hay assets ni fuentes empaquetadas; `make dist` solo copia `.py`, `locales/` y runtime.

La UI actual funciona, pero cualquier sistema nuevo obliga a tocar `ui.py`, `ui_panel.py`, `ui_modals.py` y `ui_map.py` a la vez. Ese es el problema que este plan ataca.

---

## 2. Decisiones de base

### 2.1 Grilla de 16 px y layout fijo

La pantalla 640×480 es exactamente 40×30 tiles de 16×16. El layout se alinea a esa grilla:

| Región | Medidas | Uso |
|--------|---------|-----|
| Barra superior | 640×32 | título, día/hora, vitales, alerta |
| Barra inferior | 640×32 | acciones contextuales con glifos |
| Panel lateral | 192×416 | inspección, acciones, estados |
| Mapa | 448×416 | 28×26 tiles a 16 px |

```
┌──────────────────────────────────────────────┐ 32
│ SOLITUDINE  NEP-325   Día 3 14h   O2 H2O Food ⚡│
├───────────────────────────────┬──────────────┤
│                               │ INSPECCIÓN   │
│                               │ Módulo: ...  │
│            MAPA 448×416       │ Estado: ...  │
│                               │ E: ...       │
│                               │ Buffer: ...  │
│                               │ [R1] Apagar  │
│                               │              │
├───────────────────────────────┴──────────────┤ 32
│ A=seleccionar  Y=construir  X=capa  R1=apagar│
└──────────────────────────────────────────────┘
```

- Tokens: `TILE=16`, `PAD=4`, `GAP=8`, `TOPBAR_H=32`, `BOTTOMBAR_H=32`, `PANEL_W=192`.
- Todo rectángulo sale de `ui_layout.py`; no hay medidas mágicas repartidas.
- El panel de 192 px deja espacio para iconos, estados y textos de dos líneas sin apretar.

### 2.2 Zoom entero

- Tile base 16×16. Niveles de zoom: **1× (16 px), 2× (32 px), 3× (48 px)**.
- Por defecto 1×, que equivale al tamaño actual (~15,5 px).
- Sin escalas fraccionarias: `pygame.transform.scale` (nearest), nunca `smoothscale`.
- Se pierde el zoom lejano actual (6 px). La vista general se resuelve más adelante con un **minimapa** o un modo overview de colores planos, no bajando sprites a 6 px.

### 2.3 Fuente pixel, no texto generado por IA

- Una fuente TTF pixel con cobertura Latin-1 (acentos y ñ), empaquetada en `assets/fonts/`, renderizada con `antialias=False`.
- Tamaños nativos: 16 px para cuerpo y 24 px para títulos. Sin tamaños intermedios que emborronen.
- La IA no genera texto ni glifos: los textos van en `locales/es.json` y se dibujan con la fuente.
- El modal debe partir líneas largas; los mensajes de muerte y las descripciones de tecnología lo necesitan.

### 2.4 Paleta compartida

- Paleta fija de 16–24 colores en `assets/palette.json`, espejada en `ui_theme.py`.
- Todos los assets generados se cuantizan a esa paleta en el pipeline offline.
- La UI y los sprites comparten paleta para que el mapa no parezca un collage.
- Los estados no dependen solo del color: icono + texto + forma (apagado, dañado, bloqueado, crítico).

### 2.5 UI estable, sistemas detrás

La UI no espera a que existan tecnología, inventario o combate para reservarles espacio:

- `ui_state.py`: estado solo de UI (overlay abierto, pestaña, scroll, selección, notificaciones).
- `ui_layout.py`: regiones y rects.
- `ui_widgets.py`: panel, barra, lista, pestañas, botón/glifo, texto con wrap, icono.
- `ui_assets.py`: carga y caché de sprites, fuentes y variantes escaladas.
- `ui_console.py`: overlay de consola con pestañas **Tecnología / Carga / Registro / Ayuda**.
- `ui_panel.py`: inspección con scroll y secciones; no una lista fija de líneas.
- `ui_map.py`: sprites, autotile, niebla y estados de módulo.
- `ui.py`: fachada y orden de dibujado.
- `ui_input.py` + `game_input.py`: política y acciones; la UI devuelve acciones, no muta la simulación desde el dibujado.

Las pestañas y los estados existen desde el principio aunque muestren “Sin datos todavía”. Cuando lleguen 4B/5A/5B, se rellenan sin mover el layout.

---

## 3. Assets con Genkit

### 3.1 Qué se probó

Se generaron muestras con perfiles temporales en `~/Code/genkit` (sin tocar este repo):

| Prueba | Perfil / modelo | Pedido | Resultado |
|--------|-----------------|--------|-----------|
| Terreno RD+ | `retro-diffusion/rd-plus`, `topdown_map` | 16×16 | **64×64** (el estilo fuerza un tamaño mayor) |
| Módulo RD+ | `rd-plus`, `topdown_item` | 32×32 | 32×32 RGBA con transparencia |
| Módulo RD+ | `rd-plus`, `topdown_item` | 16×16 | 16×16 RGBA, más simple |
| Tileset RD Tile | `retro-diffusion/rd-tile`, `tileset` | 16×16 | **64×80 = hoja 4×5** de tiles de 16 |

Conclusión: **RD+ no es fiable para terrenos de 16 px** (upscalea), pero sí para módulos e iconos. **RD Tile es la herramienta correcta para tilesets** y devuelve una hoja de 4×5 que se corta offline.

### 3.2 Perfiles nuevos en Genkit

Genkit es el dueño de los perfiles; Solitudine solo guarda prompts, seeds y rutas en su manifest. Crear en `~/Code/genkit/profiles/image/`:

```yaml
# solitudine-terrain.yaml
id: solitudine-terrain
modality: image
provider: replicate
model: retro-diffusion/rd-tile
approx_cost_usd: 0.02
params:
  width: 16
  height: 16
  style: tileset
  num_images: 1
  bypass_prompt_expansion: false
prompt_wrapper: >
  16-bit top-down pixel art tileset for a dark sci-fi survival game,
  limited palette, crisp pixels, seamless transitions, no text, no watermark,
  {prompt}
allow_overrides: [seed]
```

```yaml
# solitudine-module.yaml
id: solitudine-module
modality: image
provider: replicate
model: retro-diffusion/rd-plus
approx_cost_usd: 0.02
params:
  width: 32
  height: 32
  style: topdown_item
  remove_bg: true
  num_images: 1
  bypass_prompt_expansion: false
prompt_wrapper: >
  single top-down game asset icon, dark sci-fi survival style,
  limited palette, 1px outline, transparent background, centered,
  no shadow, no text, no watermark, {prompt}
allow_overrides: [seed]
```

```yaml
# solitudine-icon.yaml
id: solitudine-icon
modality: image
provider: replicate
model: retro-diffusion/rd-plus
approx_cost_usd: 0.02
params:
  width: 32
  height: 32
  style: skill_icon
  remove_bg: true
  num_images: 1
  bypass_prompt_expansion: false
prompt_wrapper: >
  single pixel-art UI icon, high contrast, simple silhouette,
  transparent background, no border, no text, no watermark, {prompt}
allow_overrides: [seed]
```

Ejemplo de corrida (Genkit escribe en la ruta indicada; el manifest vive en Solitudine):

```bash
cd ~/Code/genkit
./run.sh image --profile solitudine-terrain --project solitudine --batch terrain-v1 \
  --seed 42 \
  --prompt "alien planet ground, dark mossy soil, small stones, seamless" \
  --out ~/Code/solitudine/assets/source/terrain/ground.png
```

Notas:
- RD+ no expone `negative_prompt`; el prompt debe ser limpio y positivo.
- El perfil genérico `pixel` (256×256, `topdown_asset`, `remove_bg`) no sirve para terrenos de 16 px; sí como referencia de estilo.
- Si se itera mucho, evaluar `rd-fast` para borradores y dejar RD+ para finales. No crear perfiles de más sin necesidad.

### 3.3 Pipeline offline

```
assets/
├── manifest.json        # prompts, seeds, perfiles, cortes, hashes
├── palette.json         # 16–24 colores compartidos
├── CREDITS.md           # modelo/licencia/procedencia
├── source/              # hojas e imágenes originales de Genkit
│   ├── terrain/
│   ├── modules/
│   └── icons/
├── tiles/               # PNG finales 16×16
├── modules/             # PNG finales 16×16
├── icons/               # PNG finales 16×16 / 8×8
├── ui/                  # 9-slice y adornos (si no se dibujan por código)
└── fonts/               # fuente pixel con licencia
```

- `assets_build.py` en la raíz (respetando “todos los .py en la raíz”):
  - valida el manifest y que existan las fuentes;
  - corta hojas RD Tile según `cols/rows/tile_size`;
  - baja módulos/iconos de 32→16 con nearest y cuantiza a la paleta;
  - escribe los PNG finales y verifica hashes;
  - falla rápido si falta algo.
- `make assets` ejecuta el pipeline con `.venv/bin/python`; no usa red.
- `make dist` copia `assets/` completo y valida el manifest antes de empaquetar.
- La generación con Genkit es **manual y fuera del build** (`run.sh image --project solitudine --batch ...`); los assets finales se commitean para que el proyecto siga siendo offline.
- `make clean` no borra `assets/`: son fuente, no artefacto de build.
- No se añade Pillow: pygame-ce ya carga, recorta, escala y guarda PNG. Si el cuantizado a mano se vuelve incómodo, se justifica una dependencia aparte; no antes.

### 3.4 Manifiesto mínimo

```json
{
  "version": 1,
  "tile_size": 16,
  "palette": "assets/palette.json",
  "assets": [
    {
      "id": "terrain.ground",
      "kind": "terrain",
      "profile": "solitudine-terrain",
      "prompt": "alien planet ground, dark mossy soil, small stones, seamless",
      "seed": 42,
      "source": "assets/source/terrain/ground.png",
      "sheet": {"cols": 4, "rows": 5, "tile": 16},
      "outputs": ["assets/tiles/ground_0.png", "assets/tiles/ground_1.png"]
    },
    {
      "id": "module.solar",
      "kind": "module",
      "profile": "solitudine-module",
      "prompt": "solar panel module, dark metal frame, blue cells",
      "seed": 42,
      "source": "assets/source/modules/solar.png",
      "source_size": 32,
      "output": "assets/modules/solar.png",
      "output_size": 16
    }
  ]
}
```

El sidecar de Genkit no se copia tal cual (tiene rutas absolutas y URLs); el manifest guarda solo lo necesario para reproducir: perfil, prompt, seed y modelo.

### 3.5 Set inicial

| Categoría | Cantidad | Fuente | Notas |
|-----------|----------|--------|-------|
| Terreno | 3–4 hojas | RD Tile 16×16 | suelo, agua, roca y transiciones |
| Módulos actuales | 8 | RD+ 32→16 | hábitat, solar, radar, extractor, invernadero, mina, fabricador, almacén |
| Módulos futuros | 5–8 | RD+ 32→16 | laboratorio, electrolizador, condensador, batería, torreta, trampa |
| Iconos de recurso | 10 | RD+ 32→16 | O₂, agua, comida, energía, componentes, mineral, biomasa, quitina, aleación, núcleo |
| UI | mínimo | código/9-slice | marcos, barras, pestañas, cursor, glifos |
| Fuente | 1 | TTF OFL/CC0 | verificar acentos |

Coste orientativo: 15–25 llamadas × ~$0.02 = **$0.30–0.50** para el primer set. RD Tile rinde 20 tiles por llamada.

### 3.6 Autotile y variación

- Terreno: máscara de vecinos para agua/roca y elección de tile de transición. Es lógica determinista, no IA.
- Variación de suelo: elegir variante por hash de `(tx, ty)`, estable entre frames.
- Módulos: un sprite por tipo y estado; construcción con overlay de progreso; apagado con overlay de “off”; daño con marca de grieta (cuando exista).
- Cables: en la primera pasada se quedan como líneas pixeladas; si el mapa lo pide, se añade tile de cable con máscara de 4 bits.
- Depósitos: icono/overlay sobre el tile; la capa Recursos conserva el tinte actual.

---

## 4. Pantallas y contratos

### 4.1 Barra superior

- Día/hora y estado de alerta.
- Vitales: **O₂, agua, comida y energía** (icono + valor + barra compacta).
- Si no caben en una fila, la barra de 32 px admite dos filas de 16 px: título arriba, vitales abajo.
- Sin componentes ni botín: eso vive en Carga.
- Alerta de amenaza solo después del primer contacto (fase 5), con icono y texto, no una barra oculta.

### 4.2 Panel lateral

Secciones con scroll, en este orden:

1. Identidad del tile/módulo.
2. Estado: en línea / apagado / construyendo / desconectado / dañado / bloqueado.
3. Flujos y energía.
4. Buffer, reserva 3×3, progreso de obra.
5. Acciones contextuales (R1 apagar, reparar, etc.).
6. Si no hay selección: resumen del hábitat, capacidad de carga y próximos avisos.

### 4.3 Consola a pantalla completa (SELECT)

```
┌─────────────────────────────────────────────┐
│ CONSOLA > TECNOLOGÍA          Día 3  14h    │
├──────────────┬──────────────────┬───────────┤
│ RAMAS        │ NODOS            │ DETALLE   │
│ > Soporte    │ [x] Electrólisis │ Coste: 6  │
│   Energía    │ [ ] Condensador  │ Tiempo: 2d│
│   Logística  │ [ ] Reciclaje    │ Requiere: │
│              │                  │ Laboratorio│
│              │                  │ A=investigar│
├──────────────┴──────────────────┴───────────┤
│ L1/R1=rama  LJOY=navegar  A=investigar B=salir│
└─────────────────────────────────────────────┘
```

- Pestañas: Tecnología, Carga, Registro, Ayuda.
- Carga lista todos los items por categoría, cantidad y capacidad compartida.
- Registro guarda los últimos avisos (construcción, apagado, amenaza, daño, muerte).
- Tecnología usa el árbol de datos de la fase 4; hasta entonces muestra el esqueleto y “Sin datos”.
- La consola no redibuja el mapa: guarda un fondo estático o lo atenúa.

### 4.4 Modales

- Un solo `draw_map_modal` con marco 9-slice, título, líneas con wrap y máximo de ancho.
- Pausa, game over, muerte, construcción y confirmaciones comparten el mismo componente.
- Game over: causa + variante + días sobrevividos + reintentar.
- El modal nunca se sale del área 640×480 ni tapa la barra inferior sin querer.

### 4.5 Construcción

- Menú por categorías: Energía, Extracción, Soporte, Logística, Defensa.
- Cada entrada: icono, nombre, coste, tiempo y candado de tecnología.
- Las piezas bloqueadas se muestran en gris con “Requiere X”; no se ocultan.
- Scroll si no caben; la selección se mantiene al cambiar de categoría.

### 4.6 Estados visuales desde ya

| Estado | Aspecto |
|--------|---------|
| En línea | sprite normal |
| Apagado | sprite atenuado + glifo “off” + texto |
| Construyendo | silueta + barra de progreso |
| Desconectado | borde rojo + icono de red |
| Dañado (futuro) | grieta/parpadeo + icono de reparación |
| Bloqueado (futuro) | gris + candado + requisito |

Aunque apagado/dañado aún no tengan lógica completa, los assets, colores y helpers quedan listos.

---

## 5. Arquitectura de UI

| Archivo | Responsabilidad |
|---------|-----------------|
| `ui_theme.py` | paleta, tokens, formatos |
| `ui_layout.py` | rects de mapa, panel, barras y overlay |
| `ui_state.py` | overlay, pestaña, scroll, selección, notificaciones |
| `ui_widgets.py` | panel, barra, lista, pestañas, botón, icono, wrap |
| `ui_assets.py` | carga/caché de sprites, fuentes y escalas |
| `ui_map.py` | tiles, autotile, módulos, cables, niebla, preview |
| `ui_panel.py` | inspección con secciones y scroll |
| `ui_console.py` | Tecnología / Carga / Registro / Ayuda |
| `ui_modals.py` | modal 9-slice y wrap |
| `ui.py` | fachada y orden de dibujado |
| `ui_input.py` | política de input por overlay |
| `game_input.py` | acciones del jugador; no dibuja |

Reglas:
- Ningún `pygame.draw.rect` de layout fuera de `ui_theme`/`ui_widgets`/`ui_map`.
- Ningún texto hardcodeado: todo pasa por `t()`.
- La UI solo lee estado; las acciones se devuelven a `game.py` para aplicarlas.
- No crear un framework de widgets: funciones y dataclasses pequeñas.
- `ui_state` no se guarda en la partida; es efímero. La causa/variante de muerte sí se guarda.

---

## 6. Plan por etapas

### UI-0 — Base y assets (sin cambiar gameplay)

- `ui_layout.py` con la grilla 640×480/16 px.
- Tokens y paleta única; fuente pixel con acentos.
- `assets_build.py`, manifest, `make assets`, `make dist` con assets.
- Crear los 3 perfiles de Genkit y generar el primer set (terreno, 8 módulos, iconos base).
- `ui_assets.py` con caché y escalas 1×/2×/3×.
- `ui_map.py` dibuja sprites en lugar de rects; niebla y depósitos se mantienen.
- Criterio: el juego se ve pixel art, sigue jugable y no cambia ninguna regla.

### UI-1 — Shell y HUD

- Barra superior con O₂/agua/comida/energía.
- Barra inferior con acciones y glifos.
- Panel con secciones, scroll y estados.
- `Module.enabled` visual (aunque la lógica llegue en 4A): sprite atenuado y glifo.
- Modales con marco 9-slice y wrap.
- Criterio: 640×480 sin solapes; textos largos se parten; APAGADO se ve claro; R36S legible.

### UI-2 — Consola y huecos futuros

- `ui_console.py` con pestañas Tecnología/Carga/Registro/Ayuda.
- Placeholders de tecnología, inventario, amenaza y daño.
- Menú de construcción por categorías con candados.
- Game over con causa y días; el hueco de variante queda listo para 5A.
- Notificaciones básicas en Registro.
- Criterio: se puede navegar toda la consola con mando; los sistemas futuros solo rellenan datos.

### UI-3 — Pulido

- Autotile de agua/roca y variación de terreno.
- Animaciones cortas (construcción, alerta, apagado).
- Minimapa/overview para compensar el zoom mínimo de 16 px.
- Pruebas de rendimiento y capturas de regresión.
- Criterio: 60 FPS en PC y estable en R36S; sin escalado por frame.

### Después de UI-2

- **4A** aporta `enabled`, guardado y tests; la UI ya tiene el estado visual.
- **4B** rellena la pestaña Tecnología.
- **4C/5A** rellenan Carga e inventario.
- **5B** rellena amenaza/combate y el registro.

---

## 7. Riesgos y mitigaciones

| Riesgo | Prob. | Impacto | Mitigación |
|--------|-------|---------|------------|
| Assets de IA inconsistentes | Alta | Medio | Paleta fija, seeds, manifest, cuantizado, retoque manual |
| RD+ ignora el tamaño pedido | Media | Alto | Terreno con RD Tile; validar dimensiones en el pipeline |
| UI reescrita de más y retrasa el juego | Media | Alto | UI-0/1 sin cambiar reglas; juego jugable tras cada etapa |
| Texto ilegible en 3.5" | Media | Alto | Fuente pixel 16/24, contraste, probar en R36S |
| Escalado borroso | Media | Medio | Zoom entero y nearest; caché de escalas |
| Fuente sin acentos/ñ | Media | Medio | Verificar Latin-1 antes de elegir |
| Sin assets por red/coste | Baja | Alto | Assets finales commiteados; Genkit solo en desarrollo |
| Licencia de modelos/assets | Baja | Medio | `CREDITS.md` y verificación de licencia |
| UI acoplada a datos futuros | Media | Medio | `ui_state`, placeholders y secciones; no lógica en dibujado |
| Pipeline añade dependencia | Media | Medio | Usar pygame; no Pillow salvo justificación |
| Zoom mínimo 16 px limita la vista | Media | Medio | Minimapa/overview en UI-3 |
| Autotile se vuelve un sistema | Media | Medio | Empezar por agua/roca; cables siguen siendo líneas |

---

## 8. Criterios de aceptación

- **UI-0:** `make assets` es offline y determinista; `make dist` incluye `assets/`; todos los tiles/módulos se dibujan desde PNG; el juego sigue jugable.
- **UI-1:** la grilla suma 640×480 sin solapes; la barra superior muestra O₂/agua/comida/energía; el panel hace scroll; los textos largos se parten; el estado apagado se distingue sin depender solo del color.
- **UI-2:** la consola se abre con SELECT y se navega con mando; las pestañas tienen contenido o placeholder; el menú de construcción muestra categorías y candados; el game over muestra causa + días y deja el slot de variante.
- **UI-3:** autotile visible en agua/roca; minimapa/overview; 60 FPS en PC; capturas de regresión para mapa, panel, consola, construcción y muerte.

---

## 9. Decisiones abiertas

1. Fuente exacta (Pixel Operator, m5x7, otra) y cobertura de acentos.
2. ¿Módulos finales 16×16 directos o 32→16? Recomendación: 32 de origen, 16 final, nearest.
3. ¿Se commitean las hojas fuente o solo los PNG finales? Recomendación: ambas; son pequeños y permiten reprocesar.
4. ¿Autotile en UI-1 o UI-3? Recomendación: UI-3, después de que el shell esté estable.
5. ¿Minimapa o modo overview con colores planos? Recomendación: minimapa en UI-3.
6. ¿Marco de paneles por código o 9-slice generado? Recomendación: código/9-slice simple, no IA.
7. ¿Animaciones? Recomendación: solo construcción, apagado y alerta; nada que bloquee la lectura.
8. ¿RD Fast para borradores? Recomendación: solo si RD+ se vuelve lento/caro; no duplicar perfiles.
9. ¿Se permite zoom <16 px con LOD de colores? Recomendación: no en esta etapa; minimapa.
10. ¿La paleta es de 16 o 24 colores? Recomendación: 24 para cubrir terreno + UI + alertas.

---

## 10. Próximo paso concreto

1. Añadir los 3 perfiles en `~/Code/genkit` (fuera de este repo).
2. Generar el primer set: 3–4 hojas de terreno, 8 módulos y 10 iconos; guardar fuentes y `assets/manifest.json`.
3. UI-0: `ui_layout.py`, tokens, `assets_build.py`, `ui_assets.py` y sprites en el mapa.
4. Playtest corto; después UI-1 y UI-2.

No abrir UI-2 hasta que UI-0 y UI-1 estén cerradas y probadas en R36S.
