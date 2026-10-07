# EvalIA

Evaluación reproducible de modelos y prompts en español. El objetivo es comparar salidas con respuestas revisadas y mostrar aciertos, errores, evidencia, tiempo y costo bajo condiciones documentadas.

## Estado del proyecto

Proyecto en etapa inicial. Los pasos 0, 1, 2 y 3 están completados. Existen un contrato de datos, diez casos ficticios y un paquete Python instalable con validación, normalizadores, métricas deterministas y una línea base por reglas. Nueve casos están revisados y uno está marcado para revisión por un conflicto deliberado. Los comandos de ejecución y comparación, así como los paneles descritos en el plan, son entregables futuros.

La primera tarea será extraer fecha de cierre, modalidad, habilidades obligatorias y requisito de ser estudiante de fragmentos de convocatorias. La primera versión usará Ollama localmente, tendrá una interfaz web local para ejecutar experimentos y una demo pública de resultados precomputados.

## Documentación

- [Plan de implementación](plans/evalia-implementation.md): alcance, secuencia, dependencias y criterios de cierre.
- [Bitácora](docs/progress.md): subtareas realizadas, verificaciones y siguiente trabajo.
- [Modo de contribución](CONTRIBUTING.md): ramas, commits y revisión de cambios.
- [Guía de anotación](docs/annotation-guide.md): significado de los campos y reglas de evidencia.
- [Normalización](docs/normalization.md): fechas, vocabulario de habilidades, versiones y límites.
- [Rúbrica de evaluación](docs/scoring.md): puntaje por campo, denominadores y exclusiones.
- [Línea base y reporte](docs/baseline.md): reglas, resultados del conjunto inicial y reproducción.
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
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\ruff check .
.\.venv\Scripts\python scripts\generate_seed_baseline.py --check
```

`evalia validate` comprueba la sintaxis JSONL, el esquema 0.1.0, la unicidad de IDs y textos, las posiciones y el contenido literal de las citas, la correspondencia entre habilidades y evidencias, y el vocabulario canónico. Informa línea, caso y campo de los errores detectados. Las funciones de normalización convierten candidatos sin modificar el archivo de referencia. Una cita literal correcta no acredita por sí sola que respalde semánticamente el valor anotado; esa revisión sigue siendo humana.

La licencia de distribución del código sigue pendiente de definición. La publicación del repositorio no constituye una autorización de reutilización de textos de terceros.
