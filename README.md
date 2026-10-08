# EvalIA

Evaluación reproducible de modelos y prompts en español. El objetivo es comparar salidas con respuestas revisadas y mostrar aciertos, errores, evidencia, tiempo y costo bajo condiciones documentadas.

## Estado del proyecto

Proyecto en desarrollo. Los pasos 0 a 4 y la subtarea 5.1 están completados. Existen un contrato de datos, diez casos ficticios, validación, normalizadores, métricas deterministas, una línea base por reglas y un motor de ejecución incremental con proveedor simulado y adaptador Ollama local. Nueve casos están `reviewed`; `seed-008` conserva el estado `review_required` por un conflicto deliberado y no se ejecuta ni puntúa.

La primera tarea es extraer fecha de cierre, modalidad, habilidades obligatorias y requisito de ser estudiante de fragmentos de convocatorias. La primera versión tendrá una interfaz web local para ejecutar experimentos y una demo pública de resultados precomputados.

| Etapa | Estado | Resultado o siguiente entrega |
| --- | --- | --- |
| 0. Contrato y casos | Completa | Esquema autoritativo, guía y diez casos ficticios con revisión documentada. |
| 1. Repositorio | Completa | Paquete Python, CLI y pruebas locales sin proveedores pagados. |
| 2. Validación | Completa | JSONL, coherencia de citas y normalización versionada. |
| 3. Evaluación | Completa | Métricas auditables y línea base por reglas, sin resultados atribuidos a modelos. |
| 4. Motor | Completa | Proveedor simulado, artefactos incrementales, límites y reintentos. |
| 5.1. Ollama local | Completa | Adaptador HTTP de loopback y prueba de humo de los nueve casos revisados. |
| 5.2. Conjunto inicial | Siguiente | Ampliar a 30–40 casos revisados y separar desarrollo/prueba final. |
| 6–8. Comparación y paneles | Pendiente | Comparación, exportación segura, panel local y demo pública. |
| 9. OpenRouter | Optativa | Solo tras comprobar costo, seguridad y utilidad del recorrido local. |

La [bitácora](docs/progress.md) contiene las verificaciones y el [plan](plans/evalia-implementation.md) fija el alcance de cada entrega. Esta tabla se actualizará con cada subtarea.

## Documentación

- [Plan de implementación](plans/evalia-implementation.md): alcance, secuencia, dependencias y criterios de cierre.
- [Bitácora](docs/progress.md): subtareas realizadas, verificaciones y siguiente trabajo.
- [Modo de contribución](CONTRIBUTING.md): ramas, commits y revisión de cambios.
- [Guía de anotación](docs/annotation-guide.md): significado de los campos y reglas de evidencia.
- [Normalización](docs/normalization.md): fechas, vocabulario de habilidades, versiones y límites.
- [Rúbrica de evaluación](docs/scoring.md): puntaje por campo, denominadores y exclusiones.
- [Línea base y reporte](docs/baseline.md): reglas, resultados del conjunto inicial y reproducción.
- [Motor y proveedores](docs/runner.md): contrato compartido, ejecución sin red, persistencia y límites.
- [Contrato de ejecuciones](schemas/evalia-run.schema.json): manifiesto y registros de respuestas 0.3.0.
- [Prompt de ejemplo](prompts/extraction-v1.json) y [fixture simulado](examples/fixtures/seed-two.json): entradas reproducibles para `evalia run`.
- [Contrato de casos](schemas/evalia-case.schema.json): estructura autoritativa del formato 0.1.0.
- [Casos de arranque](datasets/README.md): diez ejemplos ficticios, decisiones de anotación y estado de revisión.
- [Registro de revisión](docs/seed-review.md): procedimiento, decisiones y evidencia de la segunda lectura.

## Desarrollo

El trabajo avanza en subtareas pequeñas. Cada entrega conserva su verificación y describe las decisiones necesarias para continuar en otra sesión. El repositorio seguirá las guías relevantes del plugin ECC instalado en el entorno de desarrollo.

### Entorno local de desarrollo

EvalIA requiere Python 3.11 o posterior. En PowerShell, crear un entorno aislado e instalar el paquete con sus herramientas de desarrollo:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
```

Si `ensurepip` falla al crear `.venv` en Windows, usar la instalación de `pip` ya disponible para preparar ese entorno:

```powershell
python -m venv --without-pip .venv
python -m pip --python .venv install -e ".[dev]"
```

Comprobar el paquete y la calidad del código:

```powershell
.\.venv\Scripts\evalia --help
.\.venv\Scripts\evalia version
.\.venv\Scripts\evalia validate datasets\seed.jsonl
.\.venv\Scripts\evalia run --dataset datasets\seed.jsonl --prompt prompts\extraction-v1.json --fixture examples\fixtures\seed-two.json --output runs\prueba-local --max-cases 2
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\ruff check .
.\.venv\Scripts\python scripts\generate_seed_baseline.py --check
```

`evalia validate` comprueba la sintaxis JSONL, el esquema 0.1.0, la unicidad de IDs y textos, las posiciones y el contenido literal de las citas, la correspondencia entre habilidades y evidencias, y el vocabulario canónico. Informa línea, caso y campo de los errores detectados. Las funciones de normalización convierten candidatos sin modificar el archivo de referencia. Una cita literal correcta no acredita por sí sola que respalde semánticamente el valor anotado; esa revisión sigue siendo humana.

### Ejecución local con Ollama

Se necesita Ollama en ejecución y un modelo ya descargado. Comprueba los nombres disponibles con `ollama list` y pasa uno de ellos a `--model-id`; el nombre debe coincidir exactamente. El adaptador usa `http://127.0.0.1:11434` de forma explícita y solo acepta direcciones HTTP de loopback. No requiere OpenRouter ni claves de API.

```powershell
.\.venv\Scripts\evalia run --provider ollama --model-id qwen3:8b --dataset datasets\seed.jsonl --prompt prompts\extraction-v1.json --output runs\ollama-local --max-cases 10 --max-output-tokens 256 --timeout-seconds 120 --max-retries 0
```

`--output` debe señalar un directorio que aún no exista. Aunque el límite sea diez, el conjunto actual envía **nueve** casos: `seed-008` sigue pendiente de revisión. El adaptador solicita JSON sin razonamiento visible, conserva la respuesta cruda, registra el digest local del modelo y deja el costo en `null` porque Ollama no informa un costo de API. Los artefactos de `runs/` son privados y Git los ignora. La salida exitosa del proveedor no demuestra que una extracción sea correcta; el paso 6 incorporará comparación y reportes de ejecuciones.

El 8 de octubre de 2026, una prueba local con `qwen3:8b` completó nueve solicitudes, sin fallos de transporte; las nueve respuestas fueron objetos JSON con las cuatro claves solicitadas. La mediana de tiempo por solicitud fue 782 ms con el modelo ya cargado. Se registraron el digest y las condiciones del equipo en la [bitácora](docs/progress.md); estas cifras son de una única máquina y no son una evaluación de calidad ni un benchmark general.

La licencia de distribución del código sigue pendiente de definición. La publicación del repositorio no constituye una autorización de reutilización de textos de terceros.
