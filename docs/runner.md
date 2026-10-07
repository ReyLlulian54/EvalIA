# Motor de ejecución — paso 4

El paso 4 une casos, prompts y proveedores. Su implementación se divide en tres entregas revisables:

| Subtarea | Estado | Alcance |
| --- | --- | --- |
| 4.1 | Completada | Contrato Python de proveedor y simulador sin red. |
| 4.2 | Completada | Motor que conserva manifiesto y respuestas de forma incremental. |
| 4.3 | Pendiente | Comando de ejecución, límites, reintentos acotados y prueba de interrupción. |

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
