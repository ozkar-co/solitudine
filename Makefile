# Solitudine — entorno de desarrollo y empaquetado para R36S (PortMaster).
#
# La consola no usa Nuitka/PyInstaller: `make dist` copia los .py y el runtime
# pygame-ce (squashfs, versionado en port/runtime/) a dist/.
# Runtime: pygame-ce_2.5.6_python_3.12.8.squashfs
#   https://github.com/viniciusfs/pygame-ce-runtime/releases/tag/v0.3.0
#   sha256 4c102f82291dc6d75ca3e6c4ab55acb2b07fc2cdeb552d961bd44aba704f2ebd
# Ejecución en PC: .venv/bin/python main.py --dev

.PHONY: config fetch clean dist

PY := .venv/bin/python
RUNTIME := port/runtime/pygame-ce_2.5.6_python_3.12.8.squashfs

config: fetch
	python3 -m venv .venv
	$(PY) -m pip install -r requirements.txt --no-index --find-links wheelhouse/

fetch:
	@if [ ! -x "$(PY)" ]; then python3 -m venv .venv; fi
	@if $(PY) -m pip download -r requirements.txt -d wheelhouse/ 2>/dev/null; then \
		echo "Wheelhouse actualizado."; \
	elif ls wheelhouse/*.whl >/dev/null 2>&1; then \
		echo "Sin red. Usando wheelhouse existente."; \
	else \
		echo "Error: sin red ni wheelhouse. Ejecutar con conexión primero." >&2; \
		exit 1; \
	fi

clean:
	rm -rf .venv dist __pycache__

dist:
	@test -f $(RUNTIME) || { echo "Error: falta $(RUNTIME)" >&2; exit 1; }
	@test -d assets || { echo "Error: falta assets/" >&2; exit 1; }
	rm -rf dist
	mkdir -p dist/solitudine/runtime dist/solitudine/locales dist/solitudine/assets
	cp *.py dist/solitudine/
	cp locales/*.json dist/solitudine/locales/
	cp -r assets/tiles assets/modules assets/icons assets/fonts dist/solitudine/assets/
	cp port/Solitudine.sh dist/Solitudine.sh
	chmod +x dist/Solitudine.sh
	cp $(RUNTIME) dist/solitudine/runtime/
	@echo "Listo: dist/"
