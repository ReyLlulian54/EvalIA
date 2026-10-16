# Puntuación privada por corrida — 6.b

`evalia score-run` puntúa una ejecución ya guardada de 5.3. No llama a modelos. El resultado queda en `score-report.json` dentro del directorio de la corrida, que debe mantenerse privado. El archivo se crea una sola vez; si existe, el comando rechaza sobrescribirlo.

```powershell
evalia score-run --dataset datasets/benchmark-v1.jsonl --prompt prompts/extraction-v1.json --run-dir runs/5-3-b-qwen3-20261015
evalia score-run --dataset datasets/benchmark-v1.jsonl --prompt prompts/extraction-v1.json --run-dir runs/5-3-c-qwen25-20261015
```

El contrato autoritativo del informe es [`evalia-score-report.schema.json`](../schemas/evalia-score-report.schema.json), versión `0.1.0`. Cada informe identifica su corrida y conserva hashes de manifiesto, registros, conjunto y prompt. Se valida el conjunto y el prompt, el estado y esquema del manifiesto, cada registro, conteos, orden de IDs, índices, hashes de lote y solicitudes e identidad informada del modelo. Solo se admite el prompt exacto de 5.3, que no solicitó citas.

El JSON crudo de cada respuesta se lee sin aceptar claves duplicadas ni constantes no estándar. Un objeto con campos faltantes o extra, tipos incorrectos o habilidades no canónicas es un `format_error`. No se corrige ni normaliza la predicción para mejorar su puntaje. Los errores del proveedor y los errores internos se conservan por separado. La cobertura usa todos los casos revisados del split como denominador; los puntajes de contenido usan solo extracciones válidas y reutilizan `grade_case`. Los contadores de habilidades y abstención siguen la [rúbrica](scoring.md). Cuando el denominador es cero, `value` es `null`. La evidencia literal queda `not_observed`; el costo no informado permanece `null`.

El informe incluye resultados por caso sin copiar texto de entrada, prompt ni respuesta cruda. `dev` y `test` tienen sus propios conteos, métricas y telemetría descriptiva. La mediana de latencia incluye la primera solicitud, que puede contener carga del modelo; no sirve por sí sola para atribuir diferencias de rendimiento. Las cuatro repeticiones `dev` no se puntúan en 6.b. La comparación pareada, la revisión semántica humana y cualquier exportación pública pertenecen a subtareas posteriores.
