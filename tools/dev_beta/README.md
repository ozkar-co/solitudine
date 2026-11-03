# Beta dev para PC

Build temporal para betatesters. **No forma parte de la distribución PortMaster/R36S** y se puede borrar cuando termine el testing.

- `main.py`: entrada sin opciones; ejecuta `game.run(dev=True, handheld=False, scale=2)`.
- `build.py`: PyInstaller onefile para el sistema actual; incluye `assets/` y `locales/`.
- `LEEME.txt`: instrucciones que viajan dentro del paquete.
- `build.sh` / `build.ps1`: crean un venv aislado `.venv-beta` e invocan `build.py`.

## Salida

- Linux: `dist/linux/SolitudineBeta` y `dist/linux/SolitudineBeta-linux.tar.gz`.
- Windows: `dist/windows/SolitudineBeta.exe` y `dist/windows/SolitudineBeta-windows.zip`.
- El ejecutable crea `saves/save.json` y `solitudine-beta.log` junto a sí mismo.
- `savegame.py` respeta `SOLITUDINE_SAVE_DIR`; solo la beta lo define.

## Build local

Linux:

```bash
./tools/dev_beta/build.sh
```

Windows (PowerShell):

```powershell
.\tools\dev_beta\build.ps1
```

## CI

`.github/workflows/dev-beta.yml` compila Linux y Windows con `workflow_dispatch` o un tag `beta-*` y sube los dos artefactos. No se dispara en cada push.

## Notas

- PyInstaller no cross-compila: Windows se genera en el runner de Windows.
- El binario Linux se compila en `ubuntu-22.04` para no exigir una glibc más nueva que la del runner.
- Es una build de testing: sin migración de saves y sin instalador.
- No agregar PyInstaller a `requirements.txt`; vive en `tools/dev_beta/requirements.txt`.
