# Beta dev para PC

Build temporal para betatesters. **No forma parte de la distribución PortMaster/R36S** y se puede borrar cuando termine el testing.

- `main.py`: beta **1x** (640×480), sin opciones.
- `bootstrap.py`: arranque compartido, log y `SOLITUDINE_SAVE_DIR`.
- `build.py`: PyInstaller onefile; incluye assets de runtime y `locales/`.
- `LEEME.txt`: instrucciones que viajan dentro del paquete.
- `build.sh` / `build.ps1`: crean un venv aislado `.venv-beta` e invocan `build.py`.

## Salida

- Local: `dist/<plataforma>/SolitudineBeta-<plataforma>.*`.
- CI en tag `v*`: GitHub Release con `Solitudine-<tag>-linux-x86_64.tar.gz`, `Solitudine-<tag>-windows-x64.zip` y `SHA256SUMS.txt`.
- Cada paquete incluye el ejecutable 1x, `LEEME.txt` y `VERSION.txt`.
- Guarda en `saves/save.json` y loguea a `solitudine-beta.log`.
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

`.github/workflows/dev-beta.yml` compila Linux y Windows con `workflow_dispatch` o un tag `v*`. En un tag, además, publica un GitHub Release con los dos paquetes versionados y `SHA256SUMS.txt`; en `workflow_dispatch` solo deja artefactos. No se dispara en cada push.

## Notas

- PyInstaller no cross-compila: Windows se genera en el runner de Windows.
- El binario Linux se compila en `ubuntu-22.04` para no exigir una glibc más nueva que la del runner.
- Es una build de testing: sin migración de saves y sin instalador.
- No agregar PyInstaller a `requirements.txt`; vive en `tools/dev_beta/requirements.txt`.
