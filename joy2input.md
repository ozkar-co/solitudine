# joy2input — notas de descubrimiento (R36S)

Documento de referencia para un futuro reemplazo de **gptokeyb** en consolas PortMaster.  
Validado con **Solitudine fase 0** (Pygame directo, sin gptokeyb).

**Hardware probado:** R36S (clone), CFW **ArkOS**, **PortMaster**, pantalla **640×480**.

---

## Por qué no usar gptokeyb (en este dispositivo)

| Problema | Detalle |
|----------|---------|
| Sticks → teclas | Pierdes rango analógico; solo direcciones digitales con repeat |
| Ejes cruzados | En este clone, lo que gptk llama `left_analog` no coincide con el stick físico izquierdo |
| Juegos con ratón | gptk no permite remapear ejes cruzados de forma fiable en la versión instalada |
| Actualizar gptk/PM | Riesgo alto: firmware incompatible, SO dañado en intentos previos |

**Conclusión:** input directo (Pygame / evdev) + remap en software propio.

---

## Arquitectura que funciona

```
Mando físico → SDL/Pygame (sin gptokeyb) → juego lee JOYBUTTON / get_axis()
```

Para ports que exigen teclado/ratón (futuro **joy2input**):

```
/dev/input/event* → joy2input → /dev/uinput (teclado/ratón virtual)
```

---

## Dispositivo SDL

- Aparecen **2 entradas** `play_joystick` para **un solo mando** físico.
- Usar **`joy0`** como dispositivo principal; el segundo suele estar idle.
- Mantener `SDL_GAMECONTROLLERCONFIG` de PortMaster (`get_controls`) por si ayuda con botones en otros clones.

---

## Mapeo de botones (confirmado)

Cruceta expuesta como **botones**, no como `JOYHATMOTION`.

| btn | Nombre |
|-----|--------|
| 0 | A |
| 1 | B |
| 2 | X |
| 3 | Y |
| 4 | L1 |
| 5 | R1 |
| 6 | L2 |
| 7 | R2 |
| 8 | SELECT |
| 9 | START |
| 11 | L3 |
| 12 | R3 |
| 13 | FN |
| 14 | DPAD_UP |
| 15 | DPAD_DOWN |
| 16 | DPAD_LEFT |
| 17 | DPAD_RIGHT |

**Hueco:** btn **10** no usado en este modelo.

---

## Ejes analógicos (confirmado — clone cruzado)

Valores **-1.0 … +1.0** vía `joy.get_axis(n)`. Deadzone recomendada: **0.15**.

En esta consola los sticks están **cruzados entre sí** y además **algunos sentidos van invertidos** respecto al estándar Xbox. No usar nombres SDL “left/right stick”; usar esta tabla:

### Stick físico izquierdo

| Dirección | axis | Signo |
|-----------|------|-------|
| Arriba | **3** | negativo |
| Abajo | **3** | positivo |
| Derecha | **0** | positivo |
| Izquierda | **0** | negativo |

### Stick físico derecho

| Dirección | axis | Signo |
|-----------|------|-------|
| Arriba | **1** | positivo |
| Abajo | **1** | negativo |
| Derecha | **2** | negativo |
| Izquierda | **2** | positivo |

### Resumen del cruce

- El stick **izquierdo** usa ejes **0 y 3** (no 0 y 1).
- El stick **derecho** usa ejes **1 y 2** (no 2 y 3).
- Los ejes **1 y 2** pertenecen al stick derecho; el **3** al izquierdo en vertical.
- Inversiones no uniformes: p. ej. stick derecho, arriba = axis 1 **+**, derecha = axis 2 **−**.

### Config de ejemplo (joy2input)

```ini
[sticks]
# Stick físico izquierdo
left_x_axis  = 0
left_y_axis  = 3
left_y_invert = true    # arriba = negativo en hardware

# Stick físico derecho
right_x_axis = 2
right_y_axis = 1
right_x_invert = true   # derecha = negativo en hardware
right_y_invert = false  # arriba = positivo en hardware

deadzone = 0.15
```

---

## Pantalla y PortMaster (Pygame)

| Tema | Valor |
|------|-------|
| Resolución | 640×480 |
| Runtime | `pygame-ce_2.5.6_python_3.12.8.squashfs` (~22 MB, obligatorio) |
| ArkOS | `SDL_VIDEODRIVER=kmsdrm` |
| Display | `pygame.SCALED \| pygame.NOFRAME` |
| Fuentes | `pygame.font.Font(None, size)` — no `SysFont` |
| Salir | Atajo de la consola / PortMaster |

Pantalla negra con juego vivo: **Options → Advanced → Change Ports SDL**.

---

## gptokeyb vs input directo

| | gptokeyb | Input directo |
|--|----------|---------------|
| Botones | Teclas simuladas | `JOYBUTTON*` |
| Sticks | Teclas / ratón limitado | Ejes + remap |
| Ejes cruzados | No corregible | Tabla por consola |
| Juegos Python | Innecesario | Ideal |
| Juegos binarios (mouse) | Único recurso oficial | **joy2input** (uinput) |

---

## Objetivos del futuro joy2input

1. Leer mando por **evdev**.
2. Aplicar **remap** de ejes según config por modelo (esta tabla para R36S clone).
3. Inyectar ratón/teclado vía **uinput**.
4. Perfiles por juego: sensibilidad, deadzone, stick → cursor.
5. No depender de actualizar firmware/gptk.

Piezas Linux: `/dev/input/event*`, `/dev/uinput`, `REL_X`/`REL_Y` o `ABS_X`/`ABS_Y`.

---

## Errores ya vistos

| Error | Fix |
|-------|-----|
| `No module named 'pygame'` | Runtime squashfs en `runtime/` |
| Pantalla negra | `kmsdrm`, `SCALED\|NOFRAME` |
| Solo teclas, cero ejes | Quitar `$GPTOKEYB` |
| `SysFont` / `fc-list` | `Font(None, …)` |

---

*Validado en Solitudine fase 0 — R36S clone, botones y ejes OK.*
