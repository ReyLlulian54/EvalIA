# Integración del visor público — 8.c

La [demo de 8.b](public-demo-ui.md) se instala desde el checkout y consume solamente el [reporte aprobado](../examples/results/benchmark-v1-qwen3-vs-qwen25.json). El [esquema público 0.1.1](../schemas/evalia-public-report.schema.json) sigue siendo el único contrato de datos. Esta entrega comprueba instalación limpia, aislamiento de inferencia y el flujo de CI; no publica la demo.

## Dependencias y ejecución local

[`requirements.txt`](../requirements.txt) contiene `-e .[panel]`: instala el paquete y el extra de Streamlit desde la raíz del repositorio, donde permanece la ruta fija del reporte. `pyproject.toml` conserva las versiones admitidas. Esta configuración hace repetible el procedimiento de instalación; **no congela versiones transitivas exactas**. Un wheel trasladado fuera del checkout no dispone de la ruta del reporte y no es el formato de publicación de esta etapa.

En un entorno virtual nuevo, desde la raíz:

```powershell
python -m pip install -r requirements.txt -e ".[dev]"
python -m pip check
python -m pytest -q
python -m ruff check .
python -m streamlit run app/public_app.py --server.address 127.0.0.1 --server.port 8502 --server.headless true
```

El último comando sirve para comprobar el arranque local y se detiene con Ctrl+C. No se necesitan Ollama, claves ni una ejecución nueva del benchmark.

## Puertas automáticas

El [flujo de GitHub Actions](../.github/workflows/ci.yml) se ejecuta en PR hacia `main` y en `push` a `main` con Python 3.11. Instala desde `requirements.txt` y el extra de desarrollo, comprueba dependencias, ejecuta la suite y Ruff. Tiene `contents: read`, no persiste credenciales del checkout, no recibe secretos de inferencia y no incluye un paso de despliegue. Las acciones están fijadas a SHA verificadas.

La [prueba de aislamiento](../tests/panel/test_public_isolation.py) revisa las importaciones del punto de entrada, lector y validador; además ejecuta `AppTest` y un filtro con puertas cerradas para importaciones del motor, lectura de `runs/` y `work/`, y sockets externos. El canal interno `socketpair` de asyncio queda permitido para que Streamlit pueda ejecutar la prueba. Las pruebas existentes conservan hash, esquema, aprobación, `null`/`false`, errores y denominadores.

La publicación por URL, la licencia del código y la verificación final de permisos pertenecen a **8.d**. La integración de esta PR no equivale a un despliegue ni acredita calidad de producción de los modelos.
