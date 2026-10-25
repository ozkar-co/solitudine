# Solitudine — entorno de desarrollo y empaquetado para la consola.
#
# La consola NO usa Nuitka/PyInstaller: `make port` copia los .py y el runtime
# pygame-ce (squashfs) a dist/solitudine/, que se traslada a la SD.
# Ejecución en PC (no hay `make run`):  .venv/bin/python main.py --dev

.PHONY: config fetch runtime clean port

PY := .venv/bin/python
RUNTIME := pygame-ce_2.5.6_python_3.12.8.squashfs
RUNTIME_URL := https://github.com/viniciusfs/pygame-ce-runtime/releases/download/v0.3.0/$(RUNTIME)

config: fetch
	python3 -m venv .venv
	$(PY) -m pip install -r requirements.txt --no-index --find-links wheelhouse/

fetch:
	@if python3 -m pip download -r requirements.txt -d wheelhouse/ 2>/dev/null; then \
		echo "Wheelhouse actualizado."; \
	elif ls wheelhouse/*.whl >/dev/null 2>&1; then \
		echo "Sin red. Usando wheelhouse existente."; \
	else \
		echo "Error: sin red ni wheelhouse. Ejecuta con conexión primero." >&2; \
		exit 1; \
	fi

runtime:
	@mkdir -p port/runtime
	@if [ -f port/runtime/$(RUNTIME) ]; then \
		echo "Ya existe: port/runtime/$(RUNTIME)"; \
	else \
		echo "Descargando runtime (~22 MB)..."; \
		curl -L --progress-bar -o port/runtime/$(RUNTIME) "$(RUNTIME_URL)"; \
	fi

clean:
	rm -rf .venv dist __pycache__

port: runtime
	rm -rf dist
	mkdir -p dist/solitudine/runtime dist/solitudine/locales
	cp *.py dist/solitudine/
	cp locales/*.json dist/solitudine/locales/
	cp port/Solitudine.sh dist/Solitudine.sh
	chmod +x dist/Solitudine.sh
	cp port/runtime/$(RUNTIME) dist/solitudine/runtime/
	@echo "Listo: dist/"
