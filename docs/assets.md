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
| `assets/tiles/forest_00.png` | placeholder procedural | — | bosque, árbol alienígena verde oscuro, 16×16 | — |
| `assets/tiles/sprout_00.png` | placeholder procedural | — | brote, tallo y hojas pequeñas, 16×16 | — |
| `assets/tiles/coast_side_00.png` | manual (no Genkit) | — | overlay 16×16 con borde de costa al oeste; se rota para N/E/S | — |
| `assets/tiles/coast_inner_corner.png` | derivado de `coast_side_00` | — | dos bordes, agua en dos lados ortogonales; base NW | — |
| `assets/tiles/coast_outer_border.png` | manual (arte del usuario) | — | punto de esquina con ambos ortogonales tierra y agua diagonal; base NW | — |
| `assets/tiles/coast_u_00.png` | derivado de `coast_side_00` | — | tres lados de agua, tierra al oeste (U/cape) | — |
| `assets/tiles/coast_parallel_00.png` | derivado de `coast_side_00` | — | agua al norte y al sur (costas paralelas) | — |
| `assets/tiles/coast_island_00.png` | derivado de `coast_side_00` | — | isla de 1×1, agua en los cuatro lados | — |
| `assets/tiles/coast_inner_outer_00.png` | derivado de `coast_inner_corner` + outer | — | inner en una esquina + outer en la diagonal opuesta; base inner NW + outer SE | — |
| `assets/tiles/ruin_00.png` | placeholder procedural | — | ruina de chatarra, piedras rotas y óxido, 16×16 | — |

La hoja RD Tile es 4 columnas × 5 filas de tiles de 16×16. Los índices no usados quedan como transiciones para un autotile futuro.

**Variación de terreno:** el render elige `ground_00`/`ground_01` por hash de coordenada y rota el tile en múltiplos de 90° para variar la textura. No hace falta duplicar assets por rotación.

**Costa (manual/derivada):** `coast_side_00.png` es la base lateral con el agua al oeste; el juego la rota para N/E/S. `coast_inner_corner` (dos bordes) y `coast_outer_border` (punto) tienen base NW y se rotan para las cuatro esquinas. `coast_inner_outer_00` combina un inner en NW con un outer en SE. `coast_u_00` tiene tierra al oeste; `coast_parallel_00` tiene agua al norte y al sur; `coast_island_00` no rota. Regla: `inner` = dos lados ortogonales de agua; `outer` = punto donde ambos ortogonales son tierra y el agua está solo en diagonal. Para agregar estilos, sumar `coast_side_01.png`, `coast_u_01.png`, etc.; el código carga todas las variantes y usa la 00 por ahora. Mantener 16×16 y alpha.

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
| `assets/modules/battery.png` | placeholder procedural | batería, carcasa metálica, barras verdes y rayo ámbar, 16×16 | — |
| `assets/modules/lamp.png` | `source/modules/lamp.png` | lamp post module, tall pole with warm glowing lamp, dark metal base, top-down view, clear silhouette | 1214 |
| `assets/modules/laboratory.png` | `source/modules/laboratory.png` | laboratory module, compact science lab, domed glass, dark metal, cyan lights, top-down | 1215 |
| `assets/modules/electrolyzer.png` | `source/modules/electrolyzer.png` | electrolysis machine, water tank and electrodes, dark metal, cyan bubbles, top-down | 1216 |
| `assets/modules/condenser.png` | `source/modules/condenser.png` | atmospheric condenser, coils and fan, dark metal, blue, top-down | 1217 |
| `assets/modules/recycler.png` | placeholder procedural | reciclador industrial, caja metálica y símbolo verde de reciclaje, 16×16 | — |
| `assets/modules/fish_trap.png` | placeholder procedural | trampa de peces, marco de madera y red, 16×16 | — |
| `assets/modules/biodiesel.png` | placeholder procedural | procesador de biodiésel, tanque y válvula, 16×16 | — |
| `assets/modules/monitor.png` | placeholder procedural | estación de monitoreo, pantalla y antena, 16×16 | — |
| `assets/modules/coal_extractor.png` | placeholder procedural | extractor de carbón, estructura y veta negra, 16×16 | — |
| `assets/modules/crystal_extractor.png` | placeholder procedural | extractor de cristales, taladro y cristal cian, 16×16 | — |
| `assets/modules/fuel_generator.png` | placeholder procedural | generador eléctrico, tanque naranja y bujía, 16×16 | — |

### Iconos

| Archivo final | Fuente 32×32 | Prompt | Seed |
|---------------|--------------|--------|------|
| `assets/icons/o2.png` | `source/icons/o2.png` | oxygen tank icon, cyan and white, simple silhouette | 1301 |
| `assets/icons/water.png` | placeholder procedural (gota) | gota de agua azul con brillo, 16×16 | — |
| `assets/icons/food.png` | `source/icons/food.png` | food ration icon, green and amber, simple silhouette | 1303 |
| `assets/icons/power.png` | `source/icons/power.png` | lightning bolt icon, yellow, simple silhouette | 1304 |
| `assets/icons/components.png` | `source/icons/components.png` | gear icon, steel and green, simple silhouette | 1305 |
| `assets/icons/mineral.png` | `source/icons/mineral.png` | mineral ore chunk icon, brown and grey, simple silhouette | 1306 |
| `assets/icons/scrap.png` | placeholder procedural | pila de chatarra, gris y marrón, 16×16 | — |
| `assets/icons/cable.png` | placeholder procedural | cable y conectores, gris, 16×16 | — |
| `assets/icons/wood.png` | placeholder procedural | tronco de madera, marrón, 16×16 | — |
| `assets/icons/coal.png` | placeholder procedural | trozo de carbón, gris oscuro, 16×16 | — |
| `assets/icons/fuel.png` | placeholder procedural | bidón de combustible, naranja, 16×16 | — |
| `assets/icons/crystal.png` | placeholder procedural | cristal cian, 16×16 | — |
| `assets/icons/biomass.png` | `source/icons/biomass.png` | green algae biomass icon, simple silhouette | 1307 |
| `assets/icons/chitin.png` | `source/icons/chitin.png` | chitin plate icon, amber, simple silhouette | 1308 |
| `assets/icons/alloy.png` | `source/icons/alloy.png` | metal alloy ingot icon, steel, simple silhouette | 1309 |
| `assets/icons/core.png` | `source/icons/core.png` | glowing crystal core icon, cyan, simple silhouette | 1310 |

Los finales de módulos e iconos son **16×16**: se bajan desde el PNG 32×32 con `pygame.transform.scale` (nearest). El source 32 se conserva para editar.

> `recycler.png`, `scrap.png`, `ruin_00.png`, `forest_00.png`, `sprout_00.png`, `fish_trap.png`, `biodiesel.png`, `monitor.png`, `coal_extractor.png`, `crystal_extractor.png`, `fuel_generator.png`, `water.png`, `cable.png`, `wood.png`, `coal.png`, `fuel.png` y `crystal.png` son placeholders procedurales; se pueden regenerar o editar a mano y actualizar seed/prompt en esta tabla.

### Créditos / easter egg

- Fuente: `assets/gatos.jpg` (foto de Neo y Cleo).
- Final: `assets/credits/gatos.png`, 640×480, pixelado desde 320×240 y reducido a una paleta de 32 colores.
- Se muestra a pantalla completa con la secuencia ↑ ↑ ↓ ↓ ← → ← → en Créditos; cualquier tecla vuelve.
- Regeneración:

```bash
magick assets/gatos.jpg -auto-orient -resize '320x240^' -gravity center -extent 320x240 \
  -dither None -colors 32 -filter point -resize 640x480 assets/credits/gatos.png
```

### Fuentes

- UI: `assets/fonts/PixelOperator.ttf` (cuerpo 16 px) y `assets/fonts/PixelOperator-Bold.ttf` (títulos 24 px), CC0 1.0 (`assets/fonts/PixelOperator-CC0.txt`).
- `assets/fonts/VT323-Regular.ttf` se conserva como fallback/A-B, SIL Open Font License 1.1 (`assets/fonts/OFL.txt`).
- Tamaños de uso: 16 px cuerpo, 24 px títulos; `antialias=False` al renderizar. El splash usa Pixel Operator Bold 48 / regular 24.
- Pixel Operator cubre Latin-1 (acentos, ñ, ¿¡); se verificó con `áéíóú ñÑ ¿? ¡!`.
- Para A/B, cambiar `FONT_BODY_FILE`, `FONT_TITLE_FILE`, `FONT_BODY_SIZE` y `FONT_TITLE_SIZE` en `ui_assets.py`.

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
