#!/bin/bash
# Lanzador PortMaster — copiar a roms/ports/Solitudine.sh

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

# Runtime pygame-ce opcional (ver README): runtime/*.squashfs
PYGAME_DIR="$HOME/pygame-ce-runtime"
PYTHON="python3"

if [ -f "$GAMEDIR/runtime/pygame-ce.squashfs" ]; then
  mkdir -p "$PYGAME_DIR"
  if [[ "$PM_CAN_MOUNT" != "N" ]]; then
    $ESUDO umount "$PYGAME_DIR" 2>/dev/null || true
  fi
  $ESUDO mount "$GAMEDIR/runtime/pygame-ce.squashfs" "$PYGAME_DIR"
  source "$PYGAME_DIR/bin/activate"
  export PYTHONHOME="$PYGAME_DIR"
  export PYTHONPATH="$PYTHONHOME/lib/python3.12"
  PYTHON="$PYGAME_DIR/bin/python"
fi

export SDL_GAMECONTROLLERCONFIG="$sdl_controllerconfig"
$GPTOKEYB "$PYTHON" -c "$GAMEDIR/solitudine.gptk" &
pm_platform_helper "$PYTHON"
"$PYTHON" "$GAMEDIR/main.py"

if [ -f "$GAMEDIR/runtime/pygame-ce.squashfs" ] && [[ "$PM_CAN_MOUNT" != "N" ]]; then
  $ESUDO umount "$PYGAME_DIR" 2>/dev/null || true
fi

pm_finish
