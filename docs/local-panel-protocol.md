# Protocolo del panel local — etapa 7

Estado: **7.a completa como diseño**, antes de implementar el controlador o la interfaz. Este documento fija el comportamiento y las pruebas de aceptación del panel. Los esquemas existentes siguen siendo la autoridad de los datos; las reglas siguientes no constituyen una implementación ni una prueba de funcionamiento.

## Subtareas y puertas

| Subtarea | Entrega | Puerta de salida |
| --- | --- | --- |
| **7.a. Diseño y contrato** | Recorrido, entradas, estados, privacidad y criterios definidos en este protocolo. | Coherencia con el motor y los contratos actuales; enlaces y diff revisados. |
| **7.b. Controlador** | Controlador Python compartido con la interfaz, sin dependencia de Streamlit: preparación, ejecución explícita, lectura y puntuación mediante funciones existentes. | Pruebas con proveedor simulado de rutas, límites, eventos repetidos, errores y conservación de artefactos. |
| **7.c. Interfaz** | `app/local_app.py`, dependencia opcional de Streamlit y arranque local documentado. | Pruebas de interacción sin inferencia real y revisión visual de formulario, estados y resultados. |
| **7.d. Verificación local** | Recorrido manual de diez casos con Ollama, auditoría de solicitudes y comprobación de escucha local. | Evidencia privada, verificaciones pertinentes y documentación de instalación y límites. |

Cada fila requiere una entrega y una PR revisables, con README, plan y bitácora actualizados. Sigue **7.b**. La demo pública corresponde al paso 8; la exportación mantiene las puertas de la etapa 6.

## Recorrido y presentación

El panel sirve a una persona que ejecuta EvalIA en su equipo. La propuesta visual inicial usa controles nativos de Streamlit, etiquetas en español, texto legible y estados expresados con palabras además de color. Las referencias visuales son opcionales. La [galería oficial de Streamlit](https://streamlit.io/gallery) puede orientar la disposición de controles y tablas.

```text
EvalIA · Panel local

1. Configurar
   Conjunto | Prompt | Nombre exacto del modelo | Límite de casos
   Opciones de generación y resumen de privacidad
   [Preparar ejecución]

2. Revisar y ejecutar
   Casos seleccionados, modelo, parámetros y destino privado
   [Ejecutar]    Estado y resultado de la operación

3. Consultar resultados
   Corrida | Conteos de ejecución | Casos y errores
   [Calcular métricas] cuando la corrida sea compatible
   Métricas por dev/test y detalles de procedencia
```

1. **Configurar:** elegir archivos locales permitidos y parámetros. Cambiar controles o enviar el formulario con Enter solo prepara y valida las entradas; no invoca al modelo.
2. **Preparar:** validar el conjunto completo y el prompt con los cargadores actuales; seleccionar los primeros casos `reviewed` hasta el límite, en el orden del archivo. Mostrar cantidad real, IDs, distribución por split, nombre del modelo, parámetros y destino. Guardar una selección preparada inmutable con hashes de las entradas. Preparar de nuevo invalida la selección anterior.
3. **Ejecutar:** un botón separado consume esa selección una sola vez. El resumen es la autoridad de lo que se enviará; cambios aún no preparados no lo modifican. Revalidar las rutas y los hashes antes de llamar al motor; si cambiaron, exigir una nueva preparación. El adaptador comprueba el nombre exacto y digest del modelo antes de crear la corrida. Durante el trabajo, mostrar «En ejecución» y deshabilitar otro inicio; no prometer porcentaje o tiempo restante que el motor no informa.
4. **Consultar:** mostrar el estado persistido, casos registrados y errores. La selección de una corrida o de un filtro nunca ejecuta ni reintenta un modelo. La puntuación es otra acción explícita y usa el puntuador existente; consultar una corrida no genera un informe nuevo.

## Entradas y configuración

| Entrada | Decisión para la primera versión del panel |
| --- | --- |
| Conjunto | Selector de archivos regulares `datasets/*.jsonl`, relativo a la raíz del checkout. Incluye `seed.jsonl` y `benchmark-v1.jsonl`; validar todo el archivo, no solo los casos seleccionados. |
| Prompt | Selector de archivos regulares `prompts/*.json`; validar esquema y exactamente un marcador `{{text}}`. Mostrar ID y versión, sin editar el archivo desde el panel. |
| Modelo | Campo de nombre exacto, inicialmente `qwen3:8b`; rechazar vacío. La existencia se comprueba con `/api/tags` al ejecutar. El panel no descarga modelos ni arranca Ollama. |
| Casos | Entero de 1 a 100, inicialmente 10. Es un máximo: `seed` envía nueve casos revisados; el benchmark permite diez. No aceptar booleanos ni fracciones como enteros. |
| Generación | Temperatura entre 0 y 2, inicialmente 0; máximo de salida entre 1 y 2048 tokens, inicialmente 256; espera de I/O entre 0.01 y 120 segundos, inicialmente 120; reintentos enteros entre 0 y 2, inicialmente 0. Rechazar valores no finitos. |
| Proveedor | Ollama en el panel. El proveedor simulado queda disponible para pruebas automáticas del controlador y la interfaz. |
| Dirección de Ollama | Fija en `http://127.0.0.1:11434`. No se hereda `OLLAMA_HOST` ni se ofrece un campo de URL o puerto. Agregar un puerto personalizado exigiría una decisión y aceptación explícitas posteriores. |
| Destino | Directorio nuevo `runs/panel/<identificador-generado>/`, asignado por el controlador. No se recibe una ruta de salida libre ni se sobrescribe una corrida. |
| Corridas consultables | Subdirectorios directos de `runs/panel/` con artefactos válidos. No hay explorador general del equipo ni importación automática de las corridas históricas. |

Los parámetros del panel adoptan los límites de la CLI, con espera inicial de 120 segundos para los modelos locales. El plazo es de I/O, no un tiempo máximo absoluto de toda la evaluación. El panel mostrará los valores efectivos antes de ejecutar. Los modelos y archivos añadidos al equipo siguen sujetos a estas validaciones.

## Contratos y reutilización

| Límite | Fuente autoritativa y responsabilidad |
| --- | --- |
| Casos | [`evalia-case.schema.json`](../schemas/evalia-case.schema.json) y el validador existente; conservar `review_status`, split y distinción entre `null` y `false`. |
| Prompt | [`evalia-prompt.schema.json`](../schemas/evalia-prompt.schema.json) y `load_prompt`; preservar identidad, versión y hash de bytes. |
| Ejecución | [`run_dataset`](../src/evalia/runner/inputs.py), [`run_requests`](../src/evalia/runner/core.py) y [`evalia-run.schema.json`](../schemas/evalia-run.schema.json) 0.3.0. El panel no compone solicitudes, reintentos ni manifiestos alternativos. |
| Puntuación | [`score_run` y `write_score_report`](../src/evalia/reports/score.py), [`evalia-score-report.schema.json`](../schemas/evalia-score-report.schema.json) 0.1.0 y [rúbrica](scoring.md). La vista consume los resultados sin recalcular métricas propias. |
| Interfaz/controlador | Un tipo Python compartido de selección preparada y un resultado tipado, definidos antes de sus consumidores en 7.b. La interfaz y el controlador se distribuyen juntos; no se crea una API HTTP ni otro esquema de artefactos. |

El tipo de selección preparada deberá conservar identificador de intención, archivos resueltos, hashes, IDs seleccionados, modelo, parámetros y destino. El resultado deberá distinguir rechazo previo, corrida con artefactos y fallo de lectura o puntuación. Las firmas y validaciones serán una única definición en el controlador, importada por `app/local_app.py`; este documento fija sus requisitos observables, no duplica tipos serializados.

**Compatibilidad de puntuación:** el puntuador de 6.b exige una corrida `completed`, el prompt congelado de aquella etapa y casos de splits `dev`/`test`. Los nombres de archivo por sí solos no acreditan compatibilidad: `score_run` verifica hashes, solicitudes, orden y conteos. Por eso una corrida sobre `seed` o con otro prompt puede ejecutarse, pero mostrará «Puntuación no disponible para estas entradas» y la razón. No se ampliará la rúbrica para eludir ese rechazo. Un fallo de puntuación conserva la corrida y nunca dispara otra inferencia.

Al calcular métricas se utiliza el mismo conjunto y prompt seleccionados para la corrida, con comprobación de procedencia. Tras reiniciar el panel, se pueden volver a seleccionar esas entradas para la auditoría; no se inventan rutas a partir de un hash. Un `score-report.json` existente se valida y se coteja con la corrida y con el resultado de la auditoría actual, sin sobrescribirlo; se comparan datos y procedencia, excluyendo únicamente la fecha `created_at` del nuevo cálculo. Toda discrepancia bloquea su presentación como informe verificado.

## Estados y prevención de ejecuciones repetidas

| Estado de la interfaz | Significado y acción permitida |
| --- | --- |
| Sin preparar | No existe selección validada. Solo se puede preparar. |
| Preparada | Resumen inmutable con intención aún no consumida. Se puede ejecutar una vez o reemplazar mediante otra preparación. |
| En ejecución | Intención consumida antes de invocar el motor. Otro clic o rerun no vuelve a despacharla. |
| Finalizada | Se consulta el manifiesto, que puede registrar errores de proveedor aunque su estado sea `completed`. |
| Rechazada | Falló la validación o la comprobación previa. Mostrar causa y acción correctiva; un nuevo intento exige preparación explícita. |
| Fallida o interrumpida | Hay artefactos parciales o un error operativo. Conservarlos, informar conteos verificables y no reanudar automáticamente. |

Estos son estados de interacción; los valores persistidos siguen siendo exclusivamente los del esquema de ejecución. Un manifiesto `running` hallado tras perder la sesión o reiniciar el servidor se muestra como estado sin cierre confirmado; no se lo cambia a `interrupted` por suposición.

El controlador debe consumir cada intención antes de la llamada con efectos y rechazar su reutilización, incluso cuando el intento falla. Debe proteger el consumo y admitir una sola ejecución activa por proceso, también entre pestañas. El destino generado se mantiene ligado a la intención; si ya existe, se rechaza sin elegir otro destino silenciosamente. Preparar una repetición deliberada crea otra intención y otro destino.

`st.session_state` conserva la selección y el resultado durante los reruns, pero **no es un registro durable**: una recarga completa reinicia la sesión. Al abrir o recargar, la aplicación parte sin ninguna orden pendiente y permite consultar artefactos; jamás reconstruye una orden de ejecución desde widgets, archivos o parámetros de URL. No se garantiza cancelar una solicitud al cerrar una pestaña. El modo soportado es un único proceso del panel local; no incluye coordinación entre varios servidores ni reanudación tras caída del proceso.

## Rutas, red y privacidad

- Fijar la raíz del checkout desde la ubicación de la aplicación. Resolver las raíces y candidatos antes de abrirlos o pasarlos al motor; comprobar pertenencia real por componentes, no por prefijo de texto. Rechazar raíces permitidas que resuelvan fuera del checkout y candidatos que salgan de su raíz, incluidos enlaces simbólicos y junctions de Windows. Repetir la comprobación al ejecutar y al consultar artefactos.
- Los selectores entregan identificadores del catálogo validado. Rechazar rutas absolutas, UNC, segmentos `..`, subdirectorios no admitidos y selecciones que ya no estén en el catálogo. Para salidas nuevas, validar el padre existente y el identificador generado; para lecturas, resolver también `manifest.json`, `responses.jsonl` y cualquier informe. El usuario local debe mantener las entradas sin cambios durante la ejecución; no se promete aislamiento frente a otro proceso local que modifique archivos simultáneamente.
- El arranque soportado de Streamlit debe fijar `server.address=127.0.0.1`, mantener CORS y XSRF activos y desactivar estadísticas de uso. El puerto web previsto es 8501; Ollama usa 11434. Configurar la URL que abre el navegador no sustituye la dirección de escucha del servidor.
- La URL cliente de Ollama tampoco demuestra dónde escucha su servidor. Antes de la prueba real se verificará el listener de Ollama; si hace falta iniciarlo, usar `OLLAMA_HOST=127.0.0.1:11434` solo para ese proceso y sin cambiar la configuración permanente.
- Mostrar conteos, IDs y códigos de error por defecto. Cualquier texto o salida cruda consultada de forma explícita se representa como texto literal, sin HTML ejecutable. Los errores de interfaz no mostrarán trazas, cuerpos HTTP ni secretos; distinguir fallo previo de corrida parcial y dar una acción concreta.
- Los artefactos permanecen bajo `runs/`, ignorado por Git. La interfaz no incorpora botones para publicar, descargar respuestas privadas ni cambiar permisos de redistribución. La lectura local no constituye autorización de publicación.

## Resultados legibles y límites

La vista de ejecución muestra estado, modelo solicitado, cantidad prevista/registrada, éxitos y fallos. «Éxito de proveedor» indica que se recibió una respuesta, no que su contenido sea correcto. La procedencia incluye hashes, digest, parámetros y commit cuando esté disponible; `source_commit=null` conserva su significado.

La vista de puntuación muestra `dev` y `test` por separado, cobertura y errores, métricas por campo con numerador/denominador y datos por caso. Un denominador cero se muestra como «No aplicable»; un costo o uso ausente como «No informado»; `false` como «No» y `null` como «Desconocido» en etiquetas de extracción. Se conserva `not_observed` para citas que el prompt no solicitó. No se añade nota compuesta ni ganador. Los tiempos describen esta máquina y esta corrida.

## Criterios de aceptación de las siguientes entregas

| ID | Escenario | Resultado exigido | Entrega |
| --- | --- | --- | --- |
| P01 | Abrir, cambiar controles, preparar o filtrar resultados | Cero llamadas de generación y cero corridas nuevas. | 7.b–c |
| P02 | Ejecutar una intención válida; repetir evento, clic o rerun | Una única invocación del motor por intención, incluso tras error; reintentos de proveedor solo según el parámetro explícito. | 7.b–c |
| P03 | Solicitudes simultáneas desde dos pestañas | Una ejecución activa por proceso; el otro inicio se rechaza sin crear una corrida. | 7.b–c |
| P04 | Recarga, sesión nueva o manifiesto sin cierre | Sin inferencia automática; artefactos preservados y estado sin cierre señalado. | 7.b–d |
| P05 | Ruta externa, traversal, raíz redirigida, symlink/junction o archivo de artefacto enlazado fuera | Rechazo antes de leer el destino externo, invocar el proveedor o crear salida. | 7.b |
| P06 | Conjunto/prompt inválido, cero revisados, parámetros fuera de rango o entradas cambiadas tras preparar | Rechazo antes de inferencia; mensaje concreto y nueva preparación cuando corresponda. | 7.b–c |
| P07 | Límite 10 en `seed` y en `benchmark-v1` | Nueve y diez IDs, respectivamente, en orden; recuento visible antes de ejecutar. | 7.b–c |
| P08 | Destino existente o archivo sin permisos | No sobrescribir; conservar archivos y comunicar el fallo. | 7.b |
| P09 | Ollama apagado, modelo ausente o respuesta de `/api/tags` inválida | Error previo legible, sin inferencia ni nueva corrida; no descargar ni iniciar servicios. | 7.b–c |
| P10 | Error de proveedor, error interno o interrupción | Respetar artefactos y estado del motor; no repetir el lote ni marcar éxito total. | 7.b–d |
| P11 | Puntuación compatible, incompatible o artefacto alterado | Reutilizar el puntuador; rechazar incompatibilidad/discrepancia, conservar la corrida y no generar solicitudes. | 7.b–c |
| P12 | `null`, `false`, errores, split vacío y citas no observadas | Etiquetas y denominadores fieles al contrato; texto crudo sin interpretación HTML. | 7.c |
| P13 | Arranque soportado en Windows | Panel y Ollama escuchan solo en loopback; configuración permanente intacta. | 7.d |
| P14 | Recorrido real de diez casos y posteriores interacciones | Diez registros auditables, una solicitud por caso con cero reintentos; filtros y reruns no crean otra corrida. | 7.d |

Las pruebas de 7.b usarán fixtures y transporte simulado. Las de 7.c usarán `streamlit.testing.v1.AppTest` con el controlador sustituido donde corresponda; un conteo de llamadas verificará P01/P02. Ninguna prueba automática llamará a modelos reales ni servicios pagados. La dependencia opcional y su versión compatible se incorporarán y comprobarán en 7.c.

Para 7.d se fijan desde ahora `benchmark-v1.jsonl`, `extraction-v1.json`, `qwen3:8b`, límite 10, temperatura 0, máximo 256 tokens, espera 120 segundos y cero reintentos. La selección actual es `bench-001` a `bench-010` (ocho `dev`, dos `test`); se comprobarán IDs, hashes y digest antes de ejecutar. Es una prueba del recorrido web, no una nueva comparación de calidad ni una ocasión para ajustar el prompt con `test`. El cierre exige auditar manifiesto y diez registros, puntuación compatible y ausencia de ejecuciones adicionales al interactuar; fallos observados se registran y resuelven antes de declarar el recorrido aceptado.

## Preparación y evidencia de 7.a

Se revisaron el plan, la bitácora y las implementaciones de carga, ejecución, Ollama y puntuación sobre `main` con la PR #33 integrada (`baa31ea3fa05bd40611f5f7a8c4b671d5320c5a8`). Se aplicaron las guías ECC `git-workflow` y `contract-first`. Context7 (`/streamlit/docs`) confirmó el envío de formularios, el reinicio de Session State al recargar, AppTest y las opciones de escucha y protección del servidor.

Referencias técnicas oficiales: [formularios](https://docs.streamlit.io/develop/concepts/architecture/forms), [Session State](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state), [AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest) y [configuración](https://docs.streamlit.io/develop/api-reference/configuration/config.toml).

**No se requiere configuración humana para 7.a ni para las pruebas simuladas de 7.b.** Antes de 7.c se instalará Streamlit en el entorno aislado como dependencia opcional; antes de 7.d se comprobarán Ollama y el modelo. Si el entorno impide esas operaciones, se informará el bloqueo y los pasos precisos para resolverlo. Esta entrega solo documenta el diseño: P01–P14 siguen pendientes de sus respectivas implementaciones y verificaciones.
