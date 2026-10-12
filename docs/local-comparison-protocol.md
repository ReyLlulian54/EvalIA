# Protocolo previo a la comparación local 5.3

Estado: **fijado antes de ejecutar `benchmark-v1` con modelos**. Esta hoja define las condiciones de dos corridas principales y de una comprobación de estabilidad. Los resultados crudos se guardarán únicamente en `runs/`, excluido de Git. La puntuación y la exportación pública corresponden al paso 6.

## Subtareas y puertas

| Subtarea | Entrega verificable | Puerta para continuar |
| --- | --- | --- |
| 5.3.a. Protocolo y disponibilidad | Entradas, modelos, parámetros, criterios y límites fijados; archivos y entorno local comprobados. | Benchmark y prompt conservan sus hashes; servidor Ollama ligado a loopback antes de la primera inferencia. |
| 5.3.b. Primera corrida | `qwen3:8b` procesa el conjunto revisado y deja manifiesto y registros privados. | Auditar identidad del modelo, 36 registros, errores y estado del manifiesto sin editar entradas. |
| 5.3.c. Segunda corrida | `qwen2.5-coder:7b` procesa el mismo conjunto, prompt y límites. | Auditar los mismos campos y documentar cualquier diferencia de entorno o fallo. |
| 5.3.d. Estabilidad y cierre | Dos repeticiones adicionales de una muestra `dev` por modelo y registro técnico pareado. | Conservar los artefactos y límites para implementar `evalia compare` en el paso 6. |

Cada fila es una entrega independiente. Una falla se documenta con su artefacto; no se cambia el prompt, el conjunto ni un parámetro después de observar `test` para mejorar una cifra.

## Entradas fijadas

- Referencia: `datasets/benchmark-v1.jsonl`, versión `benchmark-v1-1.0.0`, **36 casos `reviewed`**, 27 `dev` y 9 `test`. SHA-256 LF global: `598740b54573749e6c7eb9007117f39d9fc971c7a1ee93550a44243d22c0926c`; SHA-256 LF de `test`: `86dca1777e7b3dbb4dd523d3204f797f2ed5b2f6b42d4cb7d92334ec87b40e34`. El [manifiesto](../datasets/benchmark-v1-manifest.json) y el [esquema autoritativo](../schemas/evalia-case.schema.json) mandan sobre esta descripción.
- Prompt: `prompts/extraction-v1.json`, `prompt_id=convocatorias-es`, versión `1.0.0`, SHA-256 de sus **bytes exactos** `2535a9c5f6ab590ca356647dc342958a5459f3a2685ab67523db55a9ed37c86e`. Será idéntico en ambas corridas; no se redactará una variante a partir de salidas de `test`.
- Modelos candidatos instalados localmente: `qwen3:8b` y `qwen2.5-coder:7b`. Sus manifiestos y cinco blobs por modelo están presentes sin descarga nueva. Son modelos de familias/propósitos diferentes, aunque sus archivos de capas ocupan aproximadamente 4,87 y 4,36 GiB respectivamente; cualquier diferencia de puntuación se atribuirá a **estas configuraciones concretas**, no a una familia completa. El nombre exacto y digest deberán confirmarse mediante `/api/tags` en cada corrida.

## Condiciones iguales de las dos corridas principales

| Campo | Valor fijado |
| --- | --- |
| Proveedor y destino | Ollama local en `http://127.0.0.1:11434`; sin OpenRouter ni descargas. |
| Orden y cantidad | Las 36 líneas del mismo JSONL, con `--max-cases 36`; incluye ambas particiones sin filtrar ni reordenar. |
| Prompt | La plantilla versionada indicada arriba. |
| Temperatura | `0`. |
| Límite de salida | `256` tokens por caso. |
| Tiempo de espera | `120` segundos por solicitud. |
| Reintentos | `0`; los fallos se conservan como resultados de fiabilidad, sin reintento selectivo. |
| Formato del adaptador | `stream=false`, `think=false`, `format=json`; mismos parámetros HTTP existentes para ambos modelos. |
| Persistencia | Una ruta nueva por corrida bajo `runs/`; conservar `manifest.json` y `responses.jsonl` privados. |

Se ejecutarán de forma secuencial, con el mismo equipo y sin cargas de GPU intencionales en paralelo. Antes de cada corrida se anotarán versión del servidor, digest del modelo, memoria/GPU disponible si puede consultarse y si el modelo estaba cargado. El primer caso puede incluir carga del modelo; se distinguirá de la latencia de los casos siguientes. Temperatura cero reduce variación, pero el motor no expone una semilla de Ollama: no se prometerá identidad bit a bit entre repeticiones.

## Muestra de estabilidad preseleccionada

La muestra consta del **primer caso `dev` de cada estrato de cuatro casos**: `bench-002`, `bench-005`, `bench-009`, `bench-013`, `bench-018`, `bench-021`, `bench-025`, `bench-029` y `bench-034`. Todos son `dev` y `reviewed`; se eligieron por una regla anterior a cualquier salida del benchmark. La corrida principal aporta la primera observación de cada modelo y se harán dos corridas adicionales por modelo con un JSONL derivado de esas nueve líneas, sin modificarlas. Así habrá tres observaciones por caso y configuración, y `test` no se repetirá para estabilidad. Los subconjuntos y artefactos permanecen en `work/` y `runs/`, ignorados por Git; se registrará su hash exacto.

## Verificación y límites de interpretación

Antes de inferir, ejecutar `evalia validate datasets/benchmark-v1.jsonl`, `python scripts/check_benchmark_v1.py` y comprobar el SHA-256 exacto del prompt. `evalia run` valida entradas antes de crear un directorio nuevo, exige casos `reviewed` y registra los hashes de entradas y solicitudes. Cada corrida debe conservar su `source_commit` desde un checkout limpio, `dataset_sha256`, `prompt_sha256`, `model_digest`, parámetros, estado, conteos, tiempos, tokens y respuestas crudas. Si el servicio, digest, hash o partición no coincide, se detiene la corrida antes de interpretar resultados.

El cierre técnico de 5.3 comprobará que ambas corridas solicitaron los mismos 36 IDs en el mismo orden y que sus errores se conservaron. Un manifiesto `completed` puede contener errores por caso; no se ocultarán. Los promedios o métricas de calidad requerirán el evaluador del paso 6 y deberán separar `dev` de `test`, distinguir `null` de `false` y reconocer que las citas literales no prueban respaldo semántico. Ninguna respuesta cruda se publicará automáticamente.

## Disponibilidad local observada al preparar 5.3.a

El cliente Ollama instalado informa versión `0.32.14`. Los archivos de ambos modelos candidatos están presentes, pero **no había un servidor Ollama activo** al comprobar `127.0.0.1:11434`. En esta sesión `OLLAMA_HOST=0.0.0.0`; iniciar el servidor heredando ese valor podría exponerlo en interfaces de red. Antes de 5.3.b se iniciará o verificará el servidor con `OLLAMA_HOST=127.0.0.1:11434` solo para ese proceso y se comprobará `/api/tags`. No se modifica aquí la configuración permanente de la persona usuaria ni se ejecuta inferencia. Si este entorno no puede levantarlo en loopback, la persona usuaria deberá hacerlo antes de la siguiente corrida.
