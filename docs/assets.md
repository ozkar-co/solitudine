# Assets de Solitudine

> Set generado con Genkit (Retro Diffusion). Los PNG finales viven en `assets/` y se commitean.
> Los originales 32×32 se conservan en `assets/source/` para editar o regenerar. No hay pipeline de build permanente: este documento y los sources son la receta.

## Perfiles de Genkit

Están en `~/Code/genkit/profiles/image/`:

| Perfil | Modelo | Salida | Uso |
|--------|--------|--------|-----|
| `solitudine-terrain` | `retro-diffusion/rd-tile`, `tileset` | 16×16 por tile; hoja 4×5 (64×80) | Terreno |
| `solitudine-module` | `retro-diffusion/rd-plus`, `topdown_item`, `remove_bg` | 32×32 RGBA | Módulos |
| `solitudine-icon` | `retro-diffusion/rd-plus`, `skill_icon`, `remove_bg` | 32×32 RGBA | Iconos de UI |

Los perfiles solo permiten override de `seed`. No hay `negative_prompt` en RD+; los prompts son positivos.

## Set actual

### Terreno

| Archivo final | Fuente | Tile de la hoja (col,row) | Prompt | Seed |
|---------------|--------|--------------------------|--------|------|
| `assets/tiles/ground_00.png` | `source/terrain/ground.png` | (2,1) índice 6 | alien planet ground, dark mossy green soil with small stones and patches of dry dirt, seamless top-down terrain | 1101 |
| `assets/tiles/ground_01.png` | `source/terrain/ground.png` | (0,4) índice 16 | ídem | 1101 |
| `assets/tiles/water_00.png` | `source/terrain/water.png` | (2,1) índice 6 | alien planet water, dark teal liquid with gentle ripples, seamless top-down terrain | 1102 |
| `assets/tiles/rock_00.png` | `source/terrain/rock.png` | (2,1) índice 6 | alien planet rock, grey stone with cracks and patches of moss, seamless top-down terrain | 1103 |
| `assets/tiles/rock_01.png` | `source/terrain/rock.png` | (0,3) índice 12 | ídem | 1103 |
| `assets/tiles/ruin_00.png` | placeholder procedural | — | ruina de chatarra, piedras rotas y óxido, 16×16 | — |

La hoja RD Tile es 4 columnas × 5 filas de tiles de 16×16. Los índices no usados quedan como transiciones para un autotile futuro.

### Módulos

| Archivo final | Fuente 32×32 | Prompt | Seed |
|---------------|--------------|--------|------|
| `assets/modules/habitat.png` | `source/modules/habitat.png` | habitat module, domed capsule, white and dark metal shell, small green lights | 1201 |
| `assets/modules/solar.png` | `source/modules/solar.png` | solar panel module, dark metal frame, blue photovoltaic cells | 1202 |
| `assets/modules/radar.png` | `source/modules/radar.png` | radar dish antenna module, large circular parabolic dish on a short metal tower, teal and grey, top-down view, clear silhouette | 1213 |
| `assets/modules/extractor.png` | `source/modules/extractor.png` | water extractor module, pump and pipes, dark metal, blue tank | 1204 |
| `assets/modules/greenhouse.png` | `source/modules/greenhouse.png` | greenhouse module, glass dome, green plants inside | 1205 |
| `assets/modules/mine.png` | `source/modules/mine.png` | mining rig module, drill, dark metal, amber lights | 1206 |
| `assets/modules/fabricator.png` | `source/modules/fabricator.png` | fabricator module, industrial machine, dark metal, orange lights | 1207 |
| `assets/modules/storage.png` | `source/modules/storage.png` | storage container module, stacked crates, dark metal, green stripes | 1208 |
| `assets/modules/lamp.png` | `source/modules/lamp.png` | lamp post module, tall pole with warm glowing lamp, dark metal base, top-down view, clear silhouette | 1214 |
| `assets/modules/laboratory.png` | `source/modules/laboratory.png` | laboratory module, compact science lab, domed glass, dark metal, cyan lights, top-down | 1215 |
| `assets/modules/electrolyzer.png` | `source/modules/electrolyzer.png` | electrolysis machine, water tank and electrodes, dark metal, cyan bubbles, top-down | 1216 |
| `assets/modules/condenser.png` | `source/modules/condenser.png` | atmospheric condenser, coils and fan, dark metal, blue, top-down | 1217 |
| `assets/modules/recycler.png` | placeholder procedural | reciclador industrial, caja metálica y símbolo verde de reciclaje, 16×16 | — |

### Iconos

| Archivo final | Fuente 32×32 | Prompt | Seed |
|---------------|--------------|--------|------|
| `assets/icons/o2.png` | `source/icons/o2.png` | oxygen tank icon, cyan and white, simple silhouette | 1301 |
| `assets/icons/water.png` | `source/icons/water.png` | water drop icon, blue, simple silhouette | 1302 |
| `assets/icons/food.png` | `source/icons/food.png` | food ration icon, green and amber, simple silhouette | 1303 |
| `assets/icons/power.png` | `source/icons/power.png` | lightning bolt icon, yellow, simple silhouette | 1304 |
| `assets/icons/components.png` | `source/icons/components.png` | gear icon, steel and green, simple silhouette | 1305 |
| `assets/icons/mineral.png` | `source/icons/mineral.png` | mineral ore chunk icon, brown and grey, simple silhouette | 1306 |
| `assets/icons/scrap.png` | placeholder procedural | pila de chatarra, gris y marrón, 16×16 | — |
| `assets/icons/biomass.png` | `source/icons/biomass.png` | green algae biomass icon, simple silhouette | 1307 |
| `assets/icons/chitin.png` | `source/icons/chitin.png` | chitin plate icon, amber, simple silhouette | 1308 |
| `assets/icons/alloy.png` | `source/icons/alloy.png` | metal alloy ingot icon, steel, simple silhouette | 1309 |
| `assets/icons/core.png` | `source/icons/core.png` | glowing crystal core icon, cyan, simple silhouette | 1310 |

Los finales de módulos e iconos son **16×16**: se bajan desde el PNG 32×32 con `pygame.transform.scale` (nearest). El source 32 se conserva para editar.

> `recycler.png`, `scrap.png` y `ruin_00.png` son placeholders procedurales de la fase pre-alfa; se regenerarán con Genkit y se actualizarán seed/prompt en esta tabla.

### Créditos / easter egg

- Fuente: `assets/gatos.jpg` (foto de Neo y Cleo).
- Final: `assets/credits/gatos.png`, 640×480, pixelado desde 320×240 y reducido a una paleta de 32 colores.
- Se muestra a pantalla completa con la secuencia ↑ ↑ ↓ ↓ ← → ← → en Créditos; cualquier tecla vuelve.
- Regeneración:

```bash
magick assets/gatos.jpg -auto-orient -resize '320x240^' -gravity center -extent 320x240 \
  -dither None -colors 32 -filter point -resize 640x480 assets/credits/gatos.png
```

### Fuente

- `assets/fonts/VT323-Regular.ttf`, SIL Open Font License 1.1 (`assets/fonts/OFL.txt`).
- Tamaños de uso: 16 px cuerpo, 24 px títulos; `antialias=False` al renderizar.
- VT323 cubre acentos y ñ; se verificó con `áéíóú ñÑ ¿? ¡!`.

## Regenerar un asset

1. Asegurar el perfil en Genkit y las credenciales de Replicate.
2. Ejecutar desde `~/Code/genkit`, apuntando el `--out` a `assets/source/...` de Solitudine:

```bash
cd ~/Code/genkit
./run.sh image --profile solitudine-terrain --project solitudine --batch ui-assets-v1 \
  --seed 1101 \
  --prompt "alien planet ground, dark mossy green soil with small stones and patches of dry dirt, seamless top-down terrain" \
  --out ~/Code/solitudine/assets/source/terrain/ground.png
```

3. Para terreno, cortar el tile elegido de la hoja 4×5 con pygame y guardarlo en `assets/tiles/`.
4. Para módulos/iconos, bajar de 32×32 a 16×16 con nearest y guardar en `assets/modules/` o `assets/icons/`.
5. Actualizar esta tabla si cambia prompt, seed o índice.

El sidecar `.meta.json` de Genkit no se commitea; esta tabla es el registro que importa. Los `.meta.json` actuales se pueden borrar.

## Notas

- Los sprites no se cuantizaron a una paleta fija todavía. Si hace falta cohesión, se puede hacer una pasada posterior; los sources permiten reprocesar. El easter egg de los gatos sí usa una paleta de 32 colores.
- Los assets finales se commitean; `make dist` copia `tiles/`, `modules/`, `icons/`, `fonts/` y `credits/` a `dist/solitudine/assets/`. `source/` no se copia: es para editar/regenerar.
- Coste del set actual: 26 generaciones × ~$0.02 ≈ **$0.52**.
- Si un asset no gusta: editar el PNG final o regenerar con otro seed y actualizar la tabla. No hace falta conservar un pipeline.
