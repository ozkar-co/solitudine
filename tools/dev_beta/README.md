# Beta dev para PC

Build temporal para betatesters. **No forma parte de la distribución PortMaster/R36S** y se puede borrar cuando termine el testing.

- `main.py`: beta 2x (1280×960), sin opciones.
- `main_15.py`: beta 1.5x (960×720), sin opciones.
- `bootstrap.py`: arranque compartido, log y `SOLITUDINE_SAVE_DIR`.
- `build.py`: PyInstaller onefile de ambas variantes; incluye assets de runtime y `locales/`.
- `LEEME.txt`: instrucciones que viajan dentro de cada paquete.
- `build.sh` / `build.ps1`: crean un venv aislado `.venv-beta` e invocan `build.py`.

## Salida

- Linux: `dist/linux/SolitudineBeta-linux.tar.gz` y `dist/linux/SolitudineBeta15-linux.tar.gz`.
- Windows: `dist/windows/SolitudineBeta-windows.zip` y `dist/windows/SolitudineBeta15-windows.zip`.
- Cada archivo incluye el ejecutable de esa variante y `LEEME.txt`.
- 2x guarda en `saves/save.json` y loguea a `solitudine-beta.log`; 1.5x usa `saves-1.5x/` y `solitudine-beta-1.5x.log`.
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
