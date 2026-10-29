#!/bin/bash
# Lanzador PortMaster — copiar a roms/ports/Solitudine.sh

# Splash de texto best-effort: no depende de pygame y aparece antes del runtime.
# Si el CFW mantiene EmulationStation en pantalla puede no ser visible.
show_text_splash() {
  local msg="$1"
  local tty
  local shown=0
  for tty in /dev/tty1 /dev/tty0 /dev/console; do
    if [ -w "$tty" ]; then
      printf '\033[2J\033[H\n\n\n        SOLITUDINE\n\n        %s\n' "$msg" > "$tty" 2>/dev/null && shown=1 || true
    fi
  done
  if [ "$shown" -eq 0 ]; then
    printf '\033[2J\033[H\n\n\n        SOLITUDINE\n\n        %s\n' "$msg" 2>/dev/null || true
  fi
}

show_text_splash "loading..."

RUNTIME="pygame-ce_2.5.6_python_3.12.8"
RUNTIME_FILE="${RUNTIME}.squashfs"

XDG_DATA_HOME=${XDG_DATA_HOME:-$HOME/.local/share}

if [ -d "/opt/system/Tools/PortMaster/" ]; then
  controlfolder="/opt/system/Tools/PortMaster"
elif [ -d "/opt/tools/PortMaster/" ]; then
  controlfolder="/opt/tools/PortMaster"
elif [ -d "$XDG_DATA_HOME/PortMaster/" ]; then
  controlfolder="$XDG_DATA_HOME/PortMaster"
else
  controlfolder="/roms/ports/PortMaster"
fi

source "$controlfolder/control.txt"
[ -f "${controlfolder}/mod_${CFW_NAME}.txt" ] && source "${controlfolder}/mod_${CFW_NAME}.txt"
get_controls

GAMEDIR="/$directory/ports/solitudine"
cd "$GAMEDIR" || exit 1

> "$GAMEDIR/log.txt" && exec > >(tee "$GAMEDIR/log.txt") 2>&1

if [ ! -f "$GAMEDIR/runtime/$RUNTIME_FILE" ]; then
  echo "ERROR: falta runtime pygame-ce" | tee -a "$GAMEDIR/log.txt"
  echo "Coloca $RUNTIME_FILE en roms/ports/solitudine/runtime/" | tee -a "$GAMEDIR/log.txt"
  echo "En PC: make dist" | tee -a "$GAMEDIR/log.txt"
  sleep 8
  pm_finish
  exit 1
fi

PYGAME_DIR="$HOME/pygame-ce-runtime"
mkdir -p "$PYGAME_DIR"

if [[ "$PM_CAN_MOUNT" != "N" ]]; then
  $ESUDO umount "$PYGAME_DIR" 2>/dev/null || true
fi

show_text_splash "loading..."
$ESUDO mount "$GAMEDIR/runtime/$RUNTIME_FILE" "$PYGAME_DIR"

export SDL_GAMECONTROLLERCONFIG="$sdl_controllerconfig"

# ArkOS / R36S: kmsdrm; otros CFW pueden necesitar otro driver
if [[ "$CFW_NAME" == *"ArkOS"* ]]; then
  export SDL_VIDEODRIVER=kmsdrm
fi

pm_platform_helper "$PYGAME_DIR/bin/python"

source "$PYGAME_DIR/bin/activate"
export PYTHONHOME="$PYGAME_DIR"
export PYTHONPATH="$PYTHONHOME/lib/python3.12"
export PYTHONPYCACHEPREFIX="$GAMEDIR/.pycache"

show_text_splash "loading..."
"$PYGAME_DIR/bin/python" "$GAMEDIR/main.py" --handheld

if [[ "$PM_CAN_MOUNT" != "N" ]]; then
  $ESUDO umount "$PYGAME_DIR" 2>/dev/null || true
fi

pm_finish
