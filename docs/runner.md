# Motor de ejecución — paso 4

El paso 4 une casos, prompts y proveedores. Su implementación se divide en tres entregas revisables:

| Subtarea | Estado | Alcance |
| --- | --- | --- |
| 4.1 | Completada | Contrato Python de proveedor y simulador sin red. |
| 4.2 | Pendiente | Motor que conserve manifiesto y respuestas de forma incremental. |
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

Las pruebas de 4.1 comprueban validación de parámetros, conservación de texto crudo, ausencia explícita de uso, respuestas prefijadas, errores tipados y que repr no muestre el prompt ni la respuesta. Las subtareas 4.2 y 4.3 añadirán persistencia y control de ejecución sin cambiar el significado de estos campos.
