# Comparación pareada privada — 6.c

`evalia compare` reaudita dos corridas ya puntuadas y produce un informe privado. No ejecuta modelos. La dirección es siempre **base a candidata**; invierte las rutas solo si quieres una comparación distinta. Para la pareja fijada en el [protocolo](comparison-protocol.md):

```powershell
evalia compare --dataset datasets/benchmark-v1.jsonl --prompt prompts/extraction-v1.json --base-run runs/5-3-b-qwen3-20261015 --candidate-run runs/5-3-c-qwen25-20261015 --output work/6-c-comparison.json
```

`work/` y `runs/` están excluidos de Git. Usa una ruta de salida nueva; el comando no sobrescribe archivos. El contrato autoritativo de salida es [`evalia-comparison.schema.json`](../schemas/evalia-comparison.schema.json), versión `0.1.0`.

Antes de calcular, el comando vuelve a validar conjunto, prompt, manifiestos y registros de ambas corridas mediante `score_run`; verifica que cada `score-report.json` guardado coincida con el recálculo, salvo la hora de creación. Registra el SHA-256 exacto de cada informe. Exige proveedor, conjunto, prompt, número de solicitudes, temperatura, límite de salida, espera y reintentos iguales; también IDs, particiones y orden. Los modelos, sus digests y los commits de origen quedan como procedencia y pueden diferir. Rechaza usar la misma corrida dos veces.

Por cada campo y caso comparable: `improvement` significa base incorrecta y candidata correcta; `regression`, lo contrario; `correct_tie`, ambas correctas; `incorrect_tie`, ambas incorrectas aunque los valores erróneos sean distintos. Si cualquier lado tiene error de proveedor, interno o formato, el campo es `not_comparable`. El estado y código de error permanecen visibles. Cada split (`dev` y `test`) muestra los cinco conteos y listas de IDs por campo, cobertura por lado, TP/FP/FN de habilidades y telemetría con observaciones. Los denominadores de contenido excluyen casos no comparables; la cobertura conserva todos los casos elegibles. El costo no informado sigue en `null` y `evidence_literal` en `not_observed` porque el prompt no pidió citas.

La telemetría es descriptiva: la primera solicitud puede incluir carga del modelo y la memoria GPU disponible difirió entre corridas. El informe no declara ganador ni crea puntuación compuesta. Tampoco contiene predicciones, textos, prompt ni respuestas crudas. La revisión semántica humana y la exportación segura corresponden a **6.e** y **6.d**, respectivamente; este JSON privado no es un artefacto publicable.
