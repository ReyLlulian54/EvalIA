# Controlador del panel local — 7.b

La [API Python](../src/evalia/panel/__init__.py) implementa la preparación, ejecución y consulta previstas en el [protocolo 7.a](local-panel-protocol.md). No depende de Streamlit. La interfaz web y sus pruebas de interacción corresponden a **7.c**; la comprobación de listeners y la corrida real de diez casos a **7.d**.

## Contrato compartido

[`types.py`](../src/evalia/panel/types.py) define `RunOptions`, `PreparedRun`, `RunSnapshot`, `ExecutionResult` y `PanelError`. Los artefactos mantienen sus esquemas existentes; el controlador no crea otro formato de manifiesto ni calcula métricas alternativas.

| Operación de `LocalPanelController` | Comportamiento |
| --- | --- |
| `datasets()` / `prompts()` | Catálogos locales de nombres permitidos; sin red ni escrituras. |
| `prepare(dataset_name, prompt_name, options)` | Invalida la selección anterior, valida entradas y devuelve una selección inmutable con hashes, IDs, splits, parámetros y destino nuevo. No crea directorios ni consulta Ollama. |
| `execute(prepared)` | Consume una selección auténtica una vez, revalida rutas y bytes, y llama a `run_dataset` con Ollama en `127.0.0.1:11434`. Devuelve un `ExecutionResult`. |
| `runs()` | Nombres de directorios seguros del panel; no acredita la validez de su contenido. |
| `read_run(run_name)` | Valida esquema, IDs, índices y conteos; devuelve manifiesto y registros sin `raw_text`. `include_raw=True` permite consulta explícita de texto crudo, que la futura interfaz deberá representar como texto literal. |
| `score(run_name, dataset_name, prompt_name)` | Reaudita con `score_run` y crea el informe privado mediante `write_score_report` si falta. Un informe existente debe concordar y no se sobrescribe. |
| `read_score(run_name, dataset_name, prompt_name)` | Exige un informe existente y reaudita su contenido contra las fuentes. No escribe, incluso si el archivo desaparece durante la operación. |

Las operaciones de preparación y lectura rechazan entradas mediante `PanelError`, con `code` y mensaje seguros. La ejecución distingue `rejected`, `completed`, `failed` e `interrupted`; el campo `code` aporta el motivo. `completed_with_errors` conserva los fallos de proveedor. Si una excepción ocurre después de persistir, el resultado conserva la referencia a los artefactos y su snapshot cuando se puede leer; no se presenta como un rechazo sin corrida. La interfaz deberá mostrar el mensaje seguro, nunca la traza de la excepción encadenada.

Ejemplo de **preparación sin inferencia** desde la raíz del checkout:

```python
from pathlib import Path
from evalia.panel import LocalPanelController, RunOptions

controller = LocalPanelController(Path.cwd())
prepared = controller.prepare(
    "benchmark-v1.jsonl", "extraction-v1.json", RunOptions(max_cases=10)
)
print(prepared.case_ids)  # Solo valida y selecciona.
```

La raíz es configuración confiable del proceso. En 7.c se obtendrá de la ubicación de `app/local_app.py`, nunca de un campo del navegador. La instancia del controlador y el objeto preparado deberán conservarse en la misma sesión entre reruns. `execute(prepared)` es la única operación de esta API que inicia inferencia y se conectará exclusivamente al botón explícito de ejecución.

## Intenciones y concurrencia

Una selección pertenece a una instancia del controlador y debe ser exactamente el objeto devuelto por su última preparación. Copias, objetos reconstruidos, selecciones anteriores e intenciones consumidas se rechazan. Preparar otra selección invalida la anterior, también cuando la nueva preparación falla. El `intent_id` identifica el directorio generado del panel; el `run_id` del manifiesto lo genera el motor y es una identidad distinta.

El consumo se protege con un lock por controlador. Un segundo lock, compartido por el módulo, limita a una la ejecución activa en todo el proceso, aunque haya varias sesiones. Un intento rechazado por ocupación también queda consumido y requiere otra preparación. El lock se libera al terminar o fallar; los reintentos por caso siguen siendo responsabilidad exclusiva del motor y del parámetro `max_retries`.

Una instancia recién creada no contiene intención pendiente. Consultar corridas existentes no reconstruye órdenes ni reanuda inferencias. La garantía se limita a un proceso del panel; no incluye varios servidores, recarga del código en ejecución o persistencia de sesiones tras reiniciar.

## Rutas, lectura y puntuación

[`paths.py`](../src/evalia/panel/paths.py) valida nombres de catálogo sin rutas absolutas, UNC, separadores, streams alternativos de Windows ni nombres de dispositivos reservados. Los nombres admiten letras ASCII, números, guiones, puntos y guion bajo; comienzan por letra o número. Los conjuntos y prompts son archivos directos de `datasets/` y `prompts/`; las corridas tienen nombres hexadecimales generados bajo `runs/panel/`.

Se resuelven rutas antes de comprobar su pertenencia, incluidos symlinks y junctions. Se rechazan las raíces redirigidas incluso si apuntan a otro directorio dentro del checkout. Un enlace de archivo solo se admite si resuelve a un archivo del mismo directorio autorizado. Se comprueban también las rutas de cada artefacto al leer o puntuar. Esta protección supone que otro proceso local no altera simultáneamente los archivos entre la comprobación y su uso, límite ya fijado en 7.a.

`read_run` reutiliza los lectores estrictos y validadores existentes. Las corridas completadas requieren conteos concordantes; una corrida parcial con manifiesto atrasado devuelve `manifest_counts_unconfirmed` y permite contar los registros efectivamente leídos. El estado `running` devuelve `unclosed_run` sin modificar el archivo. Archivos corruptos o líneas incompletas se rechazan para revisión; el controlador no los repara ni los elimina. Los snapshots son vistas locales, no informes de puntuación ni prueba de respaldo semántico.

La puntuación conserva el límite de 6.b: prompt congelado, splits `dev`/`test`, corrida completada y procedencia íntegra. Los informes existentes se validan y se comparan con el cálculo actual, excluyendo únicamente `created_at`; diferencias en datos o procedencia se rechazan. `null`, `false`, denominadores y `not_observed` se conservan tal como los produce el puntuador. El panel no tiene exportación ni publicación.

## Verificación de 7.b

Las [pruebas del controlador](../tests/panel/test_controller.py) usan el motor real con un proveedor sustituido y, para una respuesta de `/api/tags` inválida, el adaptador real con `httpx.MockTransport`. El fixture bloquea conexiones de sockets. No se ejecutan modelos.

| Criterios del protocolo | Evidencia en 7.b | Trabajo pendiente |
| --- | --- | --- |
| P01–P04 | Preparar/leer sin inferencia, selección consumida, dos sesiones concurrentes, nueva sesión sin orden y manifiesto sin cierre. | Eventos de navegador, dobles clics y reruns reales en 7.c–d. |
| P05 | Traversal, UNC, nombres reservados, resolución de archivos fuera de raíz y junctions reales de Windows, también tras preparar o ejecutar. | Una prueba de symlink de archivo se omite si Windows devuelve privilegio insuficiente; los escapes de archivos se prueban además mediante resolución simulada. |
| P06–P09 | Límites, tipos, entradas inválidas o modificadas, selección 9/10, destinos existentes, permisos y fallos de comprobación de Ollama. | Mensajes y controles visuales en 7.c. |
| P10–P11 | Errores de proveedor e internos, interrupciones, reintentos acotados, preservación de artefactos, puntuación compatible y rechazo de alteraciones. | Recorrido manual real en 7.d. |
| P12–P14 | Los datos conservan `null`/`false`, errores y citas no observadas. | Representación visual, escucha local y diez casos con un modelo real. |

Verificación registrada: **76 pruebas nuevas pasan y una se omite** por falta del privilegio de symlinks de archivo en Windows. Las pruebas de junctions reales sí pasan. La suite completa, Ruff, formato de archivos nuevos y comprobación del benchmark se registran en la [bitácora](progress.md). Context7 confirmó `Path.resolve` antes de comparar pertenencia y el uso de locks; se aplicaron ECC `contract-first`, `git-workflow` y `eval-harness`.

Sigue **7.c**. No se requiere configuración humana para usar las pruebas simuladas de 7.b. La instalación opcional de Streamlit se realizará al implementar la interfaz; Ollama se comprobará antes de 7.d.
