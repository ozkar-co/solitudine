$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..\..")

if (-not (Test-Path ".venv-beta")) {
  if (Get-Command py -ErrorAction SilentlyContinue) {
    py -3 -m venv .venv-beta
  } else {
    python -m venv .venv-beta
  }
}
.\.venv-beta\Scripts\python.exe -m pip install -q -r requirements.txt -r tools\dev_beta\requirements.txt
.\.venv-beta\Scripts\python.exe tools\dev_beta\build.py
