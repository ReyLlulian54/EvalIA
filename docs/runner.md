# Motor de ejecución — paso 4

El paso 4 une casos, prompts y proveedores. Su implementación se divide en tres entregas revisables:

| Subtarea | Estado | Alcance |
| --- | --- | --- |
| 4.1 | Completada | Contrato Python de proveedor y simulador sin red. |
| 4.2 | Completada | Motor que conserva manifiesto y respuestas de forma incremental. |
| 4.3 | Completada | Comando de ejecución con fixture, límites, reintentos acotados y prueba de interrupción. |

## Contrato de 4.1

La autoridad de este límite interno es [base.py](../src/evalia/providers/base.py), compartida por motor y adaptadores en el mismo paquete Python. No se duplica el contrato de extracción: cualquier contenido estructurado dentro de la respuesta cruda se validará contra el [esquema autoritativo](../schemas/evalia-case.schema.json) cuando se implemente su consumo.

| Tipo | Dato | Significado |
| --- | --- | --- |
| GenerationRequest | case_id, prompt, model_id | Identidad del caso, prompt ya compuesto e identificador exacto solicitado. El prompt queda oculto en repr para reducir divulgación accidental. |
| GenerationRequest | temperature, max_output_tokens, timeout_seconds | Configuración y límites explícitos por solicitud; se rechazan valores negativos, no finitos o límites nulos. |
| GenerationResponse | raw_text | Salida original, aunque sea vacía o JSON inválido. Queda oculta en repr. |
| GenerationResponse | reported_model_id | Identificador informado por el proveedor, si lo entrega. No se rellena con el solicitado. |
| GenerationResponse | prompt_tokens, completion_tokens, cost_usd | Uso y costo informados; None significa desconocido. El costo se representa con Decimal y deberá serializarse como texto decimal en futuros artefactos. |
| ProviderFailure | code, retryable, message | Error explícito y clasificación para una política de reintentos posterior. El mensaje no debe contener claves ni cuerpos HTTP completos. |

ModelProvider es un protocolo con provider_id y generate(request). Un adaptador puede implementarlo sin heredar de una clase base. La operación devuelve GenerationResponse o lanza ProviderFailure; esta entrega todavía no envía solicitudes, reintenta, mide latencia, crea manifiestos ni puntúa salidas.

El [proveedor simulado](../src/evalia/providers/fixture.py) recibe respuestas o errores prefijados por case_id. No inventa predicciones, tokens ni costos y no usa red. Si falta un caso, produce el error no reintentable fixture_missing. Cada fallo simulado genera una excepción nueva, útil para futuras pruebas de reintentos.

~~~python
from evalia.providers.base import GenerationRequest, GenerationResponse
from evalia.providers.fixture import FixtureProvider

provider = FixtureProvider({"caso-1": GenerationResponse(raw_text='{"skills": []}')})
response = provider.generate(
    GenerationRequest(
        case_id="caso-1",
        prompt="Extrae los campos del texto...",
        model_id="modelo-de-prueba",
        temperature=0.0,
        max_output_tokens=256,
        timeout_seconds=15.0,
    )
)
~~~

Las pruebas de 4.1 comprueban validación de parámetros, conservación de texto crudo, ausencia explícita de uso, respuestas prefijadas, errores tipados y que repr no muestre el prompt ni la respuesta. La subtarea 4.2 añade persistencia sin cambiar el significado de estos campos. El código de un fallo es un identificador estable en minúsculas; el mensaje del proveedor no se guarda en los artefactos.

## Persistencia de 4.2

[`run_requests`](../src/evalia/runner/core.py) recibe solicitudes con prompts ya compuestos, un proveedor y un directorio nuevo. Exige al menos una solicitud, identificadores de caso únicos y la misma configuración de modelo y límites en todo el lote. Rechaza un directorio existente para preservar archivos del usuario. No recompone prompts ni abre conexiones por sí mismo.

El [esquema de ejecución](../schemas/evalia-run.schema.json) 0.1.0 es la fuente autoritativa de `manifest.json` y de cada línea de `responses.jsonl`; se incluye también en la distribución Python. El manifiesto registra identificador y estado (`running`, `completed`, `failed` o `interrupted`), fechas UTC, versiones de EvalIA y Python, plataforma, proveedor, modelo solicitado, parámetros y conteos. `requests_sha256` identifica la secuencia completa de solicitudes con sus prompts mediante JSON canónico y SHA-256; cada línea lleva el hash de su solicitud. El motor no añade el prompt como campo de los artefactos, aunque una respuesta cruda podría reproducirlo. `source_commit`, `dataset_sha256` y `prompt_sha256` quedan en `null` mientras su procedencia no se haya verificado; el ensamblaje de la subtarea 4.3 deberá aportar esa información. Estos hashes no sustituyen la conservación de las entradas originales para reproducir una ejecución.

Por caso, se guarda una respuesta cruda aunque no sea JSON válido, o un fallo tipado con `error_code` y `retryable`. Los fallos inesperados reciben un código genérico; los mensajes de excepción no se escriben. El modelo informado, los tokens y el costo quedan en `null` si el proveedor no los entrega; un cero informado sigue siendo cero. El costo se serializa como texto decimal para conservar su precisión. En 4.2 hay exactamente un intento por caso; `attempts` deja preparado el contrato para 4.3.

Cada línea se valida, se escribe y se sincroniza en disco antes de avanzar. Si la escritura de una línea es parcial, el motor intenta truncarla hasta la posición anterior. El manifiesto se reemplaza de forma atómica después de cada línea. Ante un fallo del proveedor, la ejecución continúa y registra el caso fallido; ante un error inesperado o de escritura, se detiene y marca `failed` o `interrupted`. Un manifiesto puede quedar atrasado si tampoco logra escribirse tras un fallo de disco: para auditarlo, leer las líneas completas de `responses.jsonl` y comparar sus índices y conteos con el manifiesto. La subtarea 4.2 conserva la evidencia; todavía no implementa reanudación automática.

Los artefactos de ejecución pueden contener texto privado del modelo y deben permanecer en `runs/`, excluido por Git. Esta entrega se probó con el proveedor simulado, sin llamadas a modelos. La CLI, composición de prompts, reintentos y prueba de interrupción del recorrido completo corresponden a **4.3**.

## Recorrido sin red de 4.3

`evalia run` carga un conjunto JSONL, una [plantilla versionada](../schemas/evalia-prompt.schema.json) y [respuestas simuladas](../schemas/evalia-fixture.schema.json). Valida **todo** el conjunto con el contrato de casos antes de crear el directorio de salida; selecciona hasta `--max-cases` casos en estado `reviewed`, en el orden del archivo. Los casos en `draft` o `review_required` no se envían al proveedor. La plantilla debe contener exactamente un marcador `{{text}}`; se sustituye una sola vez por el texto del caso, sin interpretar las llaves que aparezcan dentro de él.

Desde la raíz del repositorio, esta prueba técnica produce artefactos privados en un directorio nuevo:

~~~powershell
.\.venv\Scripts\evalia run --dataset datasets\seed.jsonl --prompt prompts\extraction-v1.json --fixture examples\fixtures\seed-two.json --output runs\prueba-4-3 --model-id simulado-v1 --max-cases 2
~~~

El fixture incluido contiene dos respuestas **simuladas** tomadas de casos ficticios conocidos; no representa resultados de un modelo ni una medida de calidad. `evalia run` informa éxitos y fallos; sale con código 1 si algún caso terminó con error. Cada ejecución exige un directorio inexistente para evitar sobrescrituras. `runs/` está excluido de Git. Las salidas crudas pueden contener material privado o incluso repetir el prompt, por lo que no deben publicarse sin revisión.

El manifiesto y los registros usan ahora la versión **0.2.0** del [contrato de ejecución](../schemas/evalia-run.schema.json). Registran SHA-256 de los bytes exactos del conjunto, prompt y fixture; identificador y versión del prompt; modelo solicitado, límites y política de reintentos. `source_commit` solo se declara cuando el código se ejecuta desde un checkout Git limpio; en otros casos queda `null`. Un hash del conjunto completo no implica que se hayan enviado todos sus casos: `request_count`, los identificadores de los registros y `requests_sha256` describen el subconjunto ejecutado.

La CLI exige un límite explícito de 1 a 100 casos; permite 1 a 2048 tokens de salida, 0.01 a 120 segundos de espera y 0 a 2 reintentos. El motor repite únicamente `ProviderFailure(retryable=True)`, con pausas acotadas de 0.1 y 0.2 segundos; otros fallos se registran sin repetir la solicitud. `attempts` guarda el número real de intentos y una interrupción conserva los casos previos con estado `interrupted`. El tiempo de espera se valida y se entrega en cada `GenerationRequest`; el proveedor concreto debe aplicarlo a su operación de red. El fixture no realiza I/O de red ni prueba cancelación forzada de proveedores arbitrarios. Esa integración corresponde al adaptador Ollama del paso 5.

La ejecución guarda respuestas crudas y fallos, sin puntuarlas ni afirmar calidad de modelos. La comparación y publicación segura corresponden al paso 6.

## Adaptador Ollama de 5.1

`--provider ollama` usa la API HTTP de Ollama en `http://127.0.0.1:11434` de forma predeterminada. `--ollama-url` solo admite HTTP en `127.0.0.1`, `localhost` o `::1`, sin credenciales ni ruta adicional. El adaptador no toma `OLLAMA_HOST` como destino implícito. Antes de crear archivos consulta `/api/tags`, exige el nombre exacto de `--model-id` y registra el digest SHA-256 informado para ese modelo. Si no puede verificarlo, falla antes de iniciar el lote.

Cada solicitud usa `/api/chat` sin streaming, con temperatura y máximo de tokens explícitos, `think=false` y `format=json`. La configuración evita que un modelo de razonamiento consuma todo el límite de salida sin entregar contenido y pide un objeto JSON sin envoltura Markdown. El adaptador conserva el contenido original, exige que el modelo informado coincida con el solicitado y registra los conteos de tokens cuando Ollama los devuelve. El costo queda en `null`, no en cero. Un HTTP 200 con texto vacío o JSON semánticamente incorrecto sigue siendo una respuesta cruda exitosa para el motor; la validación y puntuación posteriores determinarán su utilidad.

Los fallos de conexión, espera y servidor se clasifican sin copiar cuerpos HTTP ni excepciones al artefacto. La espera se aplica a operaciones de I/O de `httpx`; no es un límite absoluto de tiempo para toda la evaluación. Los reintentos del motor siguen acotados por `--max-retries`. Las pruebas automáticas usan transporte simulado y no envían solicitudes ni consumen créditos.

El [contrato de ejecución](../schemas/evalia-run.schema.json) es ahora **0.3.0**: el manifiesto exige `model_digest`, que es el hash informado por Ollama o `null` para un proveedor que no pueda verificarlo. Esta versión cambia el manifiesto y los registros; los artefactos 0.2.0 conservan su versión anterior. `source_commit` permanece en `null` si la ejecución se realiza con cambios locales sin confirmar.
