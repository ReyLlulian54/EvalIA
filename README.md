# EvalIA

Evaluación reproducible de modelos y prompts en español. El objetivo es comparar salidas con respuestas revisadas y mostrar aciertos, errores, evidencia, tiempo y costo bajo condiciones documentadas.

## Estado del proyecto

Proyecto en etapa inicial. Los pasos 0 y 1 están completados: existe un contrato de datos, diez casos ficticios y un paquete Python instalable con una CLI mínima. Nueve casos están revisados y uno está marcado para revisión por un conflicto deliberado. Los comandos de evaluación y los paneles descritos en el plan son entregables futuros.

La primera tarea será extraer fecha de cierre, modalidad, habilidades obligatorias y requisito de ser estudiante de fragmentos de convocatorias. La primera versión usará Ollama localmente, tendrá una interfaz web local para ejecutar experimentos y una demo pública de resultados precomputados.

## Documentación

- [Plan de implementación](plans/evalia-implementation.md): alcance, secuencia, dependencias y criterios de cierre.
- [Bitácora](docs/progress.md): subtareas realizadas, verificaciones y siguiente trabajo.
- [Modo de contribución](CONTRIBUTING.md): ramas, commits y revisión de cambios.
- [Guía de anotación](docs/annotation-guide.md): significado de los campos y reglas de evidencia.
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
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\ruff check .
```

La CLI ofrece por ahora `version`. El comando `validate` se implementará en el paso 2; ejecutar `evalia validate` antes de ese paso produce un error de comando desconocido.

La licencia de distribución del código sigue pendiente de definición. La publicación del repositorio no constituye una autorización de reutilización de textos de terceros.
