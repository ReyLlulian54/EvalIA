# Visor público de solo lectura — 8.b

La demo local muestra únicamente el [reporte aprobado](../examples/results/benchmark-v1-qwen3-vs-qwen25.json) que seleccionó la revisión 6.e. Su estructura sigue el [contrato público 0.1.1](../schemas/evalia-public-report.schema.json) y las puertas del [protocolo 8.a](public-demo-protocol.md). No ejecuta modelos ni consulta `runs/` o `work/`.

## Abrir el visor durante el desarrollo

Desde la raíz del repositorio, con el extra `panel` instalado:

```powershell
.\.venv\Scripts\python -m pip install -e ".[dev,panel]"
.\.venv\Scripts\python -m streamlit run app/public_app.py --server.address 127.0.0.1 --server.port 8502
```

Abrir <http://127.0.0.1:8502>. El puerto 8502 permite mantener separado el panel local de ejecución. No se necesitan Ollama, claves, cuenta de alojamiento ni una corrida nueva. La publicación por URL pertenece a 8.d.

## Lectura y límites

El lector usa una ruta fija y exige la huella SHA-256 de los bytes, el esquema 0.1.1 y `publication_review=approved_for_publication` antes de entregar datos a la vista. Si falla una comprobación, muestra un error seguro y no cambia de fuente. No se acepta una ruta, URL o archivo del visitante.

La vista presenta por separado `dev` y `test`, con conteos y denominadores del propio reporte. Los filtros cambian solo los casos visibles; los agregados permanecen vinculados a la selección completa del artefacto. En el detalle, `false` significa una negativa explícita y `null` una ausencia o valor desconocido. Los errores de formato, proveedor o proceso no tienen predicción: el código de error se presenta como dato, no como un resultado evaluado.

Los 36 casos son ficticios y seleccionados. El artefacto no contiene texto de las convocatorias, respuestas crudas ni citas de los modelos; `not_observed` no demuestra respaldo semántico. La comparación es descriptiva, sin ganador ni afirmación de calidad de producción. La licencia del código, el alojamiento y la comprobación de la URL final siguen como puertas de 8.d.

## Verificación de la entrega

Las pruebas focalizadas del lector y `streamlit.testing.v1.AppTest` comprueban selección fija, rechazo de datos alterados, filtros, estados, errores y distinción entre `null` y `false`. La revisión visual local comprueba que el visor pueda leerse en escritorio y móvil; la integración de CI e instalación limpia pertenecen a 8.c.
