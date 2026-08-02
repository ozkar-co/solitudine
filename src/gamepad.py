"""Mapeo del mando R36S — input directo sin gptokeyb."""

DEADZONE = 0.15

BUTTONS: dict[int, str] = {
    0: "A",
    1: "B",
    2: "X",
    3: "Y",
    4: "L1",
    5: "R1",
    6: "L2",
    7: "R2",
    8: "SELECT",
    9: "START",
    11: "L3",
    12: "R3",
    13: "FN",
    14: "DPAD_UP",
    15: "DPAD_DOWN",
    16: "DPAD_LEFT",
    17: "DPAD_RIGHT",
}

# Stick físico izquierdo: X=axis0, Y=axis3 (arriba = negativo en hardware)
LEFT_STICK_X = 0
LEFT_STICK_Y = 3

# Stick físico derecho: X=axis2 (derecha = negativo), Y=axis1 (arriba = positivo)
RIGHT_STICK_X = 2
RIGHT_STICK_Y = 1

# Tras leer get_axis: multiplicar por -1 para obtener “arriba/derecha = +” lógico
LEFT_STICK_Y_INVERT = True
RIGHT_STICK_X_INVERT = True


def button_name(btn: int) -> str:
    name = BUTTONS.get(btn)
    if name:
        return f"{name} (btn{btn})"
    return f"btn{btn}"


def axis_active(value: float) -> bool:
    return abs(value) >= DEADZONE
