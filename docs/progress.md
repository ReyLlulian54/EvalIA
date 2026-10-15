# Bitácora de implementación

## 3 de octubre de 2026 — inicio del proyecto

El plan de implementación está aprobado. El repositorio se organiza en entregas pequeñas con Conventional Commits y GitHub Flow, apoyados por las guías de ECC.

### Paso 0 — contrato y casos de arranque

| Subtarea | Estado | Entregable |
| --- | --- | --- |
| 0.1. Definir contrato y guía de anotación | Completada | Esquema JSON autoritativo 0.1.0 y decisiones de anotación. |
| 0.2. Crear diez casos de arranque | Completada | Diez textos ficticios anotados, inventario y comprobación de 30 citas. |
| 0.3. Revisar los casos después de al menos 24 horas | Completada | Nueve casos revisados; conflicto de `seed-008` confirmado y excluido. |

La configuración del paquete Python pertenece al paso 1. El conjunto inicial del paso 0 será de diez casos y no representa todavía un benchmark final de modelos.

### Evidencia de arranque

- Carpeta de trabajo: repositorio local EvalIA.
- Verificación: inspección del estado de Git y lectura del plan aprobado.
- Entregable: README, instrucciones de trabajo, convenciones de contribución e inventario de subtareas.

### Entrega 0.1 — contrato y guía

Se definieron los cuatro campos de extracción, su evidencia, la procedencia del texto y el estado de revisión. Las ausencias se distinguen de negativas explícitas. Un caso contradictorio se marca para revisión y queda fuera de las métricas finales hasta resolverlo.

El esquema JSON es la fuente autoritativa de la estructura. La guía fija cómo interpretar las convocatorias y documenta qué debe verificar posteriormente el validador del paso 2. Esta entrega no declara realizada la revisión diferida ni la creación de los diez casos.

Verificación: `python scripts/check_case_contract.py` con `jsonschema` 4.26.0 comprobó el esquema Draft 2020-12, aceptó cuatro ejemplos válidos y rechazó catorce inválidos. Entre ellos: fechas imposibles, claves desconocidas, evidencias incompatibles con `null` y estados de revisión incompletos. Se revisaron enlaces locales y diferencias de Git. Las instrucciones para repetir la comprobación están en la guía.

La PR #1 de esta entrega se integró en `main`. La subtarea 0.2 continúa desde ese contrato.

### Entrega 0.2 — diez casos ficticios

Se creó `datasets/seed.jsonl` con diez convocatorias originales ficticias, valores esperados y evidencia. `datasets/README.md` registra la procedencia, las decisiones por caso y el estado de revisión. La anotación inicial distingue cierres ausentes o sin año, fecha de inicio frente a cierre, ampliación de plazo, habilidades obligatorias frente a deseables, negación frente a ausencia y modalidades alternativas. Un ejemplo multilínea incluye emojis para comprobar las posiciones Unicode.

Verificación: `python scripts/check_seed_cases.py` comprueba los diez casos contra el esquema existente, IDs y textos únicos, correspondencia uno a uno entre habilidades y evidencias, 30 citas exactas y cobertura mínima. El conjunto contiene cinco cierres no determinables y requisitos de estudiante distribuidos en cuatro `true`, tres `false` y tres `null`. También se conserva la comprobación de cuatro ejemplos válidos y catorce inválidos del contrato. No hubo llamadas a modelos ni gasto de API.

Registro de creación: `2026-10-03T05:54:00Z`. Nueve casos quedan en `draft` y uno en `review_required`; ninguno en `reviewed`. La conformidad mecánica no constituye revisión semántica ni resultados de un benchmark final.

Siguiente subtarea: 0.3, realizar la segunda lectura desde `2026-10-04T05:54:00Z`, registrar correcciones y estados de revisión. El caso contradictorio queda fuera de métricas finales mientras no se resuelva.

### Preparación 0.3 — registro de revisión

La PR #2 de los casos se integró en `main`. Se creó [el registro de revisión](seed-review.md) con hash de entrada, procedimiento de lectura, focos por caso y campos para decisiones y correcciones. Sigue el contrato existente y distingue verificación mecánica de respaldo semántico revisado por una persona.

El `2026-10-03T18:52:38Z` se comprobó la hora: habían pasado 12 horas, 58 minutos y 38 segundos desde la creación. El plan exige al menos 24 horas; por tanto, no se realizó la segunda lectura ni se aprobaron casos. La preparación mantiene los diez registros sin cambios y deja 0.3 en curso.

Verificación de preparación: el script del conjunto mantiene diez casos conformes y 30 citas exactas. Hash SHA-256 con saltos LF: `63523c2e9d52a055e06d3a561712d0c5fee3761cdf167313c8bc83487ac4040a`. Se revisaron los enlaces locales y el diff de documentación. No hubo ejecución de modelos ni gasto de API.

Esta preparación dejó habilitada la segunda lectura desde el **4 de octubre a las 02:54 en America/Santiago** (`2026-10-04T05:54:00Z`). La sección siguiente registra su ejecución y los resultados obtenidos. En ese momento, el paso 0 seguía abierto.

### Segunda lectura asistida 0.3

La segunda lectura comenzó el `2026-10-04T20:12:15Z`, 38 horas, 18 minutos y 15 segundos después de la creación. Codex reconstruyó los cuatro campos de los diez casos, los comparó con las anotaciones y revisó el respaldo semántico de las citas siguiendo la guía 0.1.0.

Resultado: nueve casos consistentes, cero correcciones propuestas y un conflicto confirmado. `seed-008` mantiene dos cierres incompatibles, `closing_date=null`, `review_required` y exclusión completa de métricas. El JSONL no cambió, por lo que conserva la versión `seed-0.1.0` y el hash `63523c2e9d52a055e06d3a561712d0c5fee3761cdf167313c8bc83487ac4040a`.

La guía exige revisión humana para el respaldo semántico. Antes de la confirmación registrada a continuación, los nueve casos continuaban en `draft` y ninguno se presentaba como aprobado. El trabajo pendiente era la validación de la persona responsable, seguida del cambio de estados, nuevo hash y comprobación mecánica.

### Cierre 0.3 — validación humana

La persona responsable confirmó explícitamente las nueve decisiones consistentes y la permanencia de `seed-008` en `review_required` el `2026-10-04T21:40:29Z`. Los casos `seed-001` a `seed-007`, `seed-009` y `seed-010` cambiaron de `draft` a `reviewed`; no se modificaron textos, valores esperados ni citas.

El cambio de estados produce la versión `seed-0.1.1` y el hash SHA-256 `5fd3ffb891ccdca1b7cdf4642af2dc7b547438eda8d3e4766e0af5a26e3ea78e`. El esquema autoritativo continúa en 0.1.0. Las comprobaciones mantienen diez casos conformes, 30 citas exactas, nueve `reviewed` y un `review_required`.

La subtarea 0.3 y el paso 0 quedan completados. El siguiente trabajo planificado es la primera subtarea del paso 1; no se inició en esta entrega.

## 4 de octubre de 2026 — paso 1 en curso

### Base instalable

| Subtarea | Estado | Entregable |
| --- | --- | --- |
| 1.1. Crear el paquete y el contrato de herramientas | Completada | Paquete `src/evalia`, metadatos, entorno aislado, pytest, Ruff y exclusiones locales. |
| 1.2. Añadir la CLI mínima y comprobar una instalación limpia | Completada | Entrada `evalia`, ayuda y comando `version`, verificados en instalación normal aislada. |

### Entrega 1.1 — esqueleto del paquete

Se creó `pyproject.toml` como fuente de configuración del paquete `evalia` 0.1.0, con Python 3.11 o posterior, backend Hatchling y grupos de desarrollo para pytest y Ruff. La distribución todavía no declara dependencias de ejecución: Typer se incorporará en 1.2 junto con la CLI que lo utilizará. El paquete exporta su versión y publica `py.typed`; una prueba comprueba que la versión en ejecución coincida con los metadatos instalados.

El entorno local usa Python 3.14.3. La creación inicial de `.venv` no pudo ejecutar `ensurepip` porque el Python base informó una ubicación incompleta; se instaló `pip` dentro del entorno mediante la opción `pip --python`, sin modificar la instalación global. Después, `python -m pip install -e .` construyó e instaló correctamente `evalia` 0.1.0.

Verificación: pytest 9.1.1 ejecutó una prueba satisfactoria; Ruff 0.16.10 no encontró problemas; la importación informó versión 0.1.0 tanto en ejecución como en metadatos; `pip check` no encontró dependencias rotas. No hubo llamadas a modelos, servicios externos de inferencia ni uso de claves.

Siguiente subtarea: 1.2, definir la interfaz mínima de la CLI, añadir Typer cuando exista ese consumidor y comprobar `evalia --help`. El paso 1 permanece abierto.

## 5 de octubre de 2026 — cierre del paso 1

### Entrega 1.2 — CLI mínima

Se declaró Typer como dependencia de ejecución y `evalia` como punto de entrada del paquete. La CLI muestra ayuda y ofrece `evalia version`, que usa la versión pública del paquete. Los comandos de validación y evaluación aún no están implementados y se rechazan como desconocidos.

La prueba inicial detectó que Typer interpreta una aplicación con un solo comando como comando raíz. Se añadió un callback raíz para conservar la estructura de subcomandos prevista. Las pruebas comprobaron ayuda, versión y rechazo de un comando no implementado.

Verificación: `python -m pytest -q` terminó con cuatro pruebas aprobadas y `ruff check .` sin errores. Se instaló el paquete sin extras de desarrollo en un entorno nuevo y aislado dentro de `work/`; `evalia --help` y `evalia version` funcionaron, y `pip --python ... check` no encontró dependencias rotas. Este equipo requirió crear el entorno sin `pip` y usar `pip --python` por la anomalía de `ensurepip` registrada en 1.1. No hubo llamadas a modelos ni uso de claves.

Las subtareas 1.1 y 1.2 completan el paso 1. El siguiente trabajo es el validador del paso 2, comenzando por una subtarea concreta que consuma el esquema autoritativo.

## 5 de octubre de 2026 — paso 2 en curso

| Subtarea | Estado | Entregable |
| --- | --- | --- |
| 2.1. Lectura JSONL y contrato estructural | Completada | CLI `validate` con errores de línea, caso y campo; esquema 0.1.0 incluido en el paquete. |
| 2.2. Coherencia de casos y citas | Completada | Identificadores y textos únicos, correspondencia y posiciones de evidencia. |
| 2.3. Normalización documentada | Completada | Fechas y vocabulario de habilidades con reglas versionadas y pruebas. |

### Entrega 2.1 — validador estructural

`evalia validate <archivo.jsonl>` lee cada línea como un objeto JSON y aplica el esquema 0.1.0 con comprobación de formatos. El esquema en `schemas/evalia-case.schema.json` sigue siendo la fuente autoritativa; el wheel incorpora ese mismo archivo como recurso para que el comando funcione fuera del repositorio. Los errores incluyen línea, identificador del caso si está disponible y campo. Un archivo vacío falla; el comando devuelve un código distinto de cero cuando hay errores.

Las pruebas cubren el conjunto inicial de diez casos, JSON mal formado en una segunda línea, fecha sin año, modalidad desconocida y la diferencia entre `student_required=false` con cita y `null` sin ella. Esta entrega no comprueba aún unicidad entre líneas, rangos de citas, correspondencia exacta de habilidades ni respaldo semántico; esas verificaciones quedan en 2.2. La normalización queda en 2.3.

Verificación: once pruebas aprobadas con pytest y Ruff sin problemas; `evalia validate datasets/seed.jsonl` informó diez casos estructuralmente válidos. Se construyó un wheel y se comprobó que el esquema empaquetado es idéntico al archivo autoritativo. La instalación de ese wheel en un entorno aislado permitió ejecutar `evalia validate` desde `work/`, fuera de la raíz del repositorio. No hubo llamadas a modelos ni uso de claves. La siguiente subtarea es **2.2**, después de revisar e integrar esta entrega.

### Entrega 2.2 — coherencia mecánica y citas

El validador genérico añade unicidad exacta de `id` y `text`, rechazo de texto compuesto solo por espacios, correspondencia uno a uno entre `expected.skills` y `evidence.skills`, y comprobación de rangos y contenido literal de las citas escalares y de habilidades. Los errores indican línea, caso, campo y, cuando corresponde, la primera línea del duplicado. Las posiciones se calculan con índices de cadena Python, según la convención Unicode de la guía.

La validación mecánica se aplica después del esquema autoritativo; los registros con errores estructurales conservan esos diagnósticos sin ejecutar reglas que requieren campos válidos. La composición mínima del conjunto inicial continúa en `scripts/check_seed_cases.py`, sin imponer sus diez casos ni su distribución de etiquetas a los conjuntos de terceros. La coincidencia literal de una cita no demuestra respaldo semántico, y la revisión humana registrada en el paso 0 conserva su significado.

Verificación: 19 pruebas aprobadas con pytest, Ruff sin errores y formato comprobado en los archivos Python modificados. Ocho pruebas negativas nuevas cubren ID y texto repetidos, texto en blanco, rango fuera del texto, cita Unicode incorrecta, habilidad sin cita, cita duplicada y rango invertido de una cita de habilidad. `evalia validate datasets/seed.jsonl` acepta los diez casos iniciales; el comprobador específico del conjunto sigue informando 30 citas exactas y el hash `5fd3ffb891ccdca1b7cdf4642af2dc7b547438eda8d3e4766e0af5a26e3ea78e`, sin cambios en los datos. La siguiente subtarea es **2.3**, normalización documentada de fechas y habilidades; no se inició aquí.

### Entrega 2.3 — normalización versionada

Se añadieron funciones puras para normalizar fechas explícitas y habilidades. Las reglas de fechas 1.0.0 aceptan ISO, día/mes/año y fecha textual española con año; una fecha reconocible sin año queda en `None`, mientras que una fecha imposible o un formato no admitido falla explícitamente. El vocabulario de habilidades 1.0.0 vive en un único archivo JSON incluido en el paquete; registra equivalencias conservadoras y conserva términos desconocidos. La normalización de listas elimina duplicados equivalentes en orden estable.

La CLI ahora señala nombres no canónicos en `expected.skills`, sin reescribir el JSONL ni las citas. El esquema de casos permanece en 0.1.0. [La documentación de normalización](normalization.md) registra formatos, ejemplos, límites y política de versión. Ni esta etapa ni las anteriores ejecutan modelos o atribuyen respaldo semántico automático a las citas.

Verificación: 40 pruebas aprobadas con pytest; Ruff y formato de los archivos Python modificados sin errores. Las pruebas cubren formatos aceptados, años faltantes, fechas imposibles, equivalencias, términos desconocidos, deduplicación y el carácter canónico de los diez casos iniciales. `evalia validate datasets/seed.jsonl` acepta los diez casos; el comprobador del contrato acepta cuatro ejemplos válidos y rechaza catorce inválidos; el comprobador del conjunto mantiene 30 citas exactas y el hash anterior. El wheel contiene el esquema y el vocabulario idénticos a sus fuentes y sus funciones se ejecutaron desde un entorno aislado fuera de la raíz del repositorio. No hubo llamadas a modelos ni uso de claves. El paso 2 concluye aquí; el siguiente trabajo planificado es el paso 3, evaluadores deterministas, en una entrega separada.

## 6 de octubre de 2026 — paso 3 en curso

| Subtarea | Estado | Entregable |
| --- | --- | --- |
| 3.1. Contrato y puntaje por caso | Completada | Extracción derivada del esquema, puntajes por campo y exclusión de casos no revisados. |
| 3.2. Métricas del conjunto | Completada | Agregación auditable, abstención, evidencia literal y clasificación de errores. |
| 3.3. Línea base y reporte | Completada | Reglas conservadoras y reporte reproducible del conjunto inicial. |

### Entrega 3.1 — rúbrica y puntaje individual

Se definió la [rúbrica](scoring.md) antes de implementar el evaluador. `grade_case` deriva la forma de la predicción de `$defs/extraction` del esquema 0.1.0, exige habilidades canónicas y valida la referencia mecánicamente. Devuelve conteos exactos por campo, `TP/FP/FN` y precisión, cobertura y F1 de habilidades. Las razones con denominador cero muestran `None` como no aplicable. `draft` y `review_required` producen una exclusión explícita sin puntuar; `false` y `null` son distintos.

Verificación: 54 pruebas aprobadas con pytest, Ruff y formato sin errores en los archivos Python modificados. `evalia validate datasets/seed.jsonl` acepta los diez casos y el comprobador específico conserva 30 citas exactas y el mismo hash del conjunto. El wheel incluye el evaluador y una copia idéntica del esquema autoritativo; desde una instalación aislada fuera de la raíz, un caso revisado devolvió `skills_exact=1/1` y `seed-008` produjo `ExcludedCase`.

Esta entrega solo puntúa un caso cada vez. No hay todavía agregación, evaluación de evidencia, línea base ni resultados de modelos. La siguiente subtarea es **3.2**.

### Entrega 3.2 — métricas del conjunto

`evaluate_dataset` empareja predicciones por `case_id` y agrega los conteos del puntaje individual. Informa cobertura, exactitud por campo, precisión/cobertura/F1 micro de habilidades, abstención por campo escalar y coincidencia literal de citas. Cada métrica conserva numerador, denominador y casos fallidos; el denominador cero produce `None`. Los casos sin revisión quedan excluidos.

Las extracciones ausentes, duplicadas o inválidas se registran como errores de formato y reducen la cobertura sin contaminar los denominadores de contenido. Una evidencia estructuralmente inválida conserva el puntaje de extracción válida, pero recibe cero aciertos literales para los valores que afirmó; una cita bien formada pero incorrecta falla como evidencia literal. La forma de extracción y citas se deriva del esquema autoritativo. Las pruebas usan predicciones sintéticas y cubren `null` frente a `false`, errores de formato, correspondencia 1:1, conteos micro y denominadores nulos. La coincidencia de caracteres no demuestra respaldo semántico.

Verificación: 64 pruebas aprobadas con pytest, Ruff sin errores y `evalia validate datasets/seed.jsonl` acepta los diez casos sin modificar el conjunto. No se llamaron modelos ni proveedores pagados, y no hay métricas atribuibles a modelos. La siguiente subtarea es **3.3**, línea base por reglas y reporte verificable del conjunto inicial; no se inició en esta entrega.

### Entrega 3.3 — línea base por reglas y reporte verificable

La línea base 0.1.0 recibe solo identificador y texto. Busca fechas de cierre explícitas, modalidad declarada, habilidades obligatorias del vocabulario versionado y requisito explícito de ser estudiante. Se abstiene ante ausencia o conflicto y genera citas literales con posiciones Unicode. Las pruebas se fijaron antes de implementarla y cubren fechas ajenas al cierre, habilidades recomendadas, negación, modalidades incompatibles, ampliaciones y textos con emoji.

El generador produce un reporte JSON determinista con predicciones, evidencia, métricas, exclusiones, errores de formato y hashes del conjunto, las reglas, el esquema y el vocabulario. La opción --check reconstruye y compara el archivo versionado; una prueba automatizada detecta si está obsoleto. El generador rechaza casos sin permiso de redistribución. La [documentación de la línea base](baseline.md) explica reglas, límites y reproducción.

En el conjunto seed-0.1.1, nueve casos revisados recibieron predicción válida y seed-008 permaneció excluido. La exactitud de cada campo fue 9/9, la F1 micro de habilidades 20/20 y la coincidencia literal 27/27; no hubo errores de formato. Estas cifras corresponden a casos ficticios conocidos durante el desarrollo y solo comprueban el recorrido técnico. No miden generalización ni resultados de modelos.

Verificación: 72 pruebas aprobadas con pytest, Ruff y formato sin errores, validación de los diez casos semilla y --check del reporte vigente. No se hicieron llamadas pagadas. El paso 3 concluye aquí. El siguiente trabajo planificado es el paso 4, motor de ejecución, en una entrega separada.

## 6 de octubre de 2026 — paso 4 en curso

| Subtarea | Estado | Entregable |
| --- | --- | --- |
| 4.1. Contrato y simulador | Completada | Interfaz de proveedor, solicitud, respuesta cruda, fallo tipado y simulador sin red. |
| 4.2. Persistencia incremental | Completada | Motor, manifiesto y respuestas/errores caso por caso. |
| 4.3. CLI y control | Completada | Ejecución CLI sin red, límites, reintentos e interrupción simulada. |

### Entrega 4.1 — límite de proveedor y simulador

Se definió un protocolo Python único entre motor y adaptadores, con solicitud que contiene caso, prompt ya compuesto, modelo y límites explícitos. La respuesta conserva texto crudo aunque no sea JSON válido; identificador informado, tokens y costo permanecen desconocidos cuando el proveedor no los entrega. Los prompts y respuestas no aparecen en la representación automática de los objetos. Los fallos tienen código y señal de reintento, sin aplicar todavía una política.

El proveedor simulado devuelve únicamente resultados prefijados por identificador y produce un fallo no reintentable cuando falta el caso. No usa red ni inventa tokens, costos o resultados de modelos. La [documentación del motor](runner.md) registra el contrato compartido y la división del paso 4. No se implementaron aún persistencia, CLI de ejecución ni adaptadores reales.

Verificación: once pruebas nuevas de contrato y simulador aprobadas; 83 pruebas en la suite completa, Ruff y formato sin errores. El reporte de la línea base sigue vigente. La siguiente subtarea es **4.2**, persistencia incremental con manifiesto, en otra entrega.

### Entrega 4.2 — persistencia incremental

El motor recibe solicitudes ya compuestas y un proveedor que cumple el contrato de 4.1. Valida un lote homogéneo antes de crear archivos y exige un directorio nuevo. Por caso conserva la respuesta cruda o un fallo clasificado, con un solo intento y tiempo medido. Una respuesta puede ser JSON inválido sin perderse; los valores de uso desconocidos siguen en `null` y el costo informado se conserva como texto decimal. Los mensajes de excepción no se guardan en los artefactos.

El nuevo [esquema de ejecución](../schemas/evalia-run.schema.json) 0.1.0 define `manifest.json` y cada registro de `responses.jsonl`. El manifiesto documenta versión, entorno, proveedor, modelo, parámetros, estado y conteos; guarda el hash de las solicitudes reales y cada registro guarda el hash de su solicitud. El commit y los hashes del conjunto y prompt permanecen en `null` hasta que un ensamblador pueda verificarlos. La escritura de cada línea se sincroniza antes de la siguiente solicitud y el manifiesto se reemplaza tras cada registro. Ante error de escritura o fallo inesperado se conservan las líneas anteriores y se marca el estado fallido cuando el manifiesto puede actualizarse. No hay reanudación automática.

Verificación: 94 pruebas aprobadas en la suite completa, incluidas 22 de motor y proveedores. Las pruebas simulan fallos del proveedor, error de escritura y línea parcial; comprueban que los casos previos persisten, que no se exponen mensajes privados y que los artefactos satisfacen el esquema. Ruff y el formato de los archivos Python modificados pasaron; la validación mecánica mantiene diez casos y el reporte versionado de la línea base sigue vigente. No se ejecutaron modelos ni se gastaron créditos de API. La construcción de un wheel independiente quedó sin comprobar en este entorno porque falta Hatchling localmente.

La subtarea siguiente es **4.3**: comando `evalia run`, composición de prompts, reintentos y límites acotados, y prueba del recorrido interrumpido con el proveedor simulado. No se inició en esta entrega.

## 7 de octubre de 2026 — cierre del paso 4

### Entrega 4.3 — CLI y control de ejecución

Se añadió `evalia run` para unir el conjunto validado, un prompt JSON versionado y respuestas prefijadas de un fixture. Los esquemas del [prompt](../schemas/evalia-prompt.schema.json) y [fixture](../schemas/evalia-fixture.schema.json) son los contratos de entrada. La CLI exige límite explícito de casos y solo envía casos `reviewed`; valida todo el conjunto antes de crear el directorio de salida. La plantilla inserta `{{text}}` una vez y conserva las llaves del texto original sin reinterpretarlas. Los fixtures de ejemplo son sintéticos y no se presentan como resultados de modelos.

El contrato de artefactos subió a 0.2.0. El manifiesto añade identidad y versión del prompt, hashes de bytes exactos del conjunto, prompt y fixture, y política de reintentos. El commit del código se registra solo cuando el checkout está limpio; `null` sigue significando procedencia no verificada. Los errores reintentables tipados reciben como máximo dos reintentos, con pausas acotadas; los definitivos y los inesperados no se repiten. La CLI devuelve código distinto de cero si algún caso falla y no imprime mensajes de excepción de proveedores. Una interrupción deja el manifiesto en `interrupted` y conserva los casos anteriores.

El tiempo de espera y los límites se validan y se incluyen en cada solicitud, pero el proveedor concreto es quien debe aplicar la cancelación de I/O. El fixture no prueba cancelación de una llamada de red. La [guía del motor](runner.md) documenta el comando, los artefactos y este límite. El paso 5 incorporará Ollama; todavía no hay ejecuciones de modelos reales ni métricas atribuibles a ellos.

Verificación: 106 pruebas aprobadas en la suite completa; Ruff, formato, validación de los diez casos iniciales, reporte de línea base y un recorrido CLI simulado comprobados localmente. Las pruebas incluyen composición de prompt, hashes de entradas, límite y exclusión de casos no revisados, reintentos transitorios, fallos definitivos, interrupción y conservación de registros ante una línea parcial. No hubo llamadas pagadas. La construcción del wheel independiente continúa sin comprobarse porque Hatchling no está disponible en este entorno. La siguiente subtarea planificada es **5.1**, adaptador local de Ollama y primera prueba de humo controlada; no se inició aquí.

## 8 de octubre de 2026 — subtarea 5.1, Ollama local

Se añadió un adaptador HTTP de Ollama que acepta únicamente un servidor de loopback, comprueba el nombre exacto del modelo en `/api/tags` y registra su digest en el manifiesto. El [contrato de ejecución](../schemas/evalia-run.schema.json) subió a 0.3.0 con `model_digest` obligatorio pero anulable para otros proveedores. El adaptador aplica espera de I/O, clasifica fallos sin copiar mensajes privados, conserva la respuesta cruda y deja el costo desconocido en `null`. `evalia run` permite seleccionar `fixture` u `ollama`; las pruebas automáticas del nuevo proveedor usan transporte simulado y no hacen llamadas de red.

La prueba local usó Ollama 0.32.14 y `qwen3:8b`, digest `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`, temperatura 0, máximo de 256 tokens, espera de 120 segundos y cero reintentos. El equipo tenía 15,56 GiB de RAM, con 4,41 GiB libres antes del lote, y una NVIDIA GeForce RTX 5060 Ti con 16.311 MiB de VRAM, 4.200 MiB libres tras cargar el modelo. Se registran estas condiciones porque los tiempos dependen del hardware y del estado de carga.

La primera consulta, con el comportamiento de razonamiento predeterminado, consumió los 256 tokens de salida y devolvió texto vacío en 67,3 segundos. Con `think=false` entregó contenido en 3,6 segundos, pero lo envolvió en Markdown. Al solicitar además `format=json`, un caso devolvió un objeto JSON con las cuatro claves en 0,83 segundos. Por eso el adaptador fija ambos parámetros y conserva la respuesta original para auditoría.

El lote final de humo solicitó hasta diez casos del conjunto semilla y ejecutó los **nueve `reviewed`**. `seed-008` sigue `review_required` y fue excluido; no se simuló ni se aprobó un décimo caso para cumplir la cifra del plan. Los nueve registros terminaron sin errores de proveedor, tuvieron contenido no vacío y fueron objetos JSON con `closing_date`, `modality`, `skills` y `student_required`. El manifiesto registra 9 solicitudes, 9 respuestas exitosas, 0 fallos y estado `completed`. La suma de tiempos por solicitud fue 6,98 segundos y la mediana 782 ms con el modelo cargado; Ollama informó 1.801 tokens de entrada y 384 de salida. `source_commit=null` porque la ejecución se realizó durante el desarrollo, con cambios sin confirmar. Los artefactos completos permanecen en `runs/`, ignorado por Git, y no se publican respuestas crudas.

Estas cifras verifican integración, formato y trazabilidad en una máquina local. No son puntajes de extracción, pruebas de generalización ni resultados de producción. La suite completa aprobó **126 pruebas** y Ruff lint no informó errores. El formato de los archivos Python de esta entrega se comprobó por separado; una comprobación global señaló archivos anteriores ajenos a 5.1, que no se modificaron para evitar ampliar el alcance. Se construyó un wheel y se comprobó que incluye el adaptador y una copia idéntica del esquema 0.3.0. No se usaron API pagadas ni se descargaron modelos. El README raíz ahora resume el avance y se mantendrá actualizado en cada entrega. GitHub Actions continúa planificado para el paso 8; esta PR se revisa con las verificaciones locales registradas aquí.

La siguiente subtarea es **5.2**, ampliar y revisar el conjunto hasta 30–40 casos con separación de desarrollo y prueba final. La revisión diferida del nuevo conjunto deberá registrarse después del plazo previsto; no se declara realizada aquí.

## 8 de octubre de 2026 — preparación 5.2.a del conjunto ampliado

Se crearon 36 convocatorias ficticias originales en `datasets/benchmark-v1.jsonl`, todas con `review_status=draft`. Los textos y las respuestas esperadas se anotaron antes de usar modelos sobre este conjunto. La partición quedó fijada en 27 casos `dev` y 9 `test` (25 %), con los IDs de prueba y el hash normalizado a LF en `datasets/benchmark-v1-manifest.json`. El esquema autoritativo de casos permanece en 0.1.0; las posiciones de evidencia se calcularon sobre cadenas Unicode de Python y se comprobaron con el validador existente.

El borrador contiene 13 fechas, 9 modalidades y 11 requisitos de estudiante no determinables; cinco casos no tienen habilidades obligatorias explícitas. Doce requisitos de estudiante son `true` y trece son `false` por negación expresa. En total, 24 de 36 casos tienen al menos un campo ausente o no determinable y hay 113 citas de valores no nulos. Los nueve estratos y sus riesgos se registran en [el diseño del benchmark](benchmark-v1.md). Son ejemplos sintéticos y no representan oportunidades reales ni resultados de modelos.

Creación del borrador y partición final registrada: `2026-10-09T02:26:36Z`, equivalente al 8 de octubre a las 23:26 en America/Santiago. Hash SHA-256 UTF-8 con saltos LF: `aac3b05a1b67ada1a9db66d703c00ee6df60a91cd9bb8865eef8954f863aad34`. Antes de fijarla se corrigió la selección de `test`, porque la primera distribución no contenía casos con habilidades obligatorias ausentes; no se había ejecutado ningún modelo. La segunda lectura solo podrá comenzar desde `2026-10-10T02:26:36Z` si no se modifica el borrador. Un cambio de texto o anotación exige actualizar versión y hash y reiniciar el intervalo para el caso afectado.

Verificación de preparación: `evalia validate datasets/benchmark-v1.jsonl` acepta los 36 casos; `scripts/check_benchmark_v1.py` confirma hash, procedencia, partición, estados y cobertura. El conjunto semilla conserva diez casos conformes y 30 citas exactas. La suite completa aprobó **126 pruebas**; Ruff lint y formato del nuevo script pasaron. No se llamaron modelos ni proveedores pagados sobre el nuevo conjunto. La validación mecánica no prueba que las 113 citas respalden semánticamente sus etiquetas.

La 5.2 **sigue abierta**. El siguiente trabajo concreto, 5.2.b, es reconstruir y contrastar semánticamente los 36 casos, repetir la lectura de al menos nueve tras 24 horas y registrar la confirmación humana. No se marcó ningún caso nuevo como `reviewed` ni se congeló el contenido final de `test`.

## 10 de octubre de 2026 — revisión asistida parcial 5.2.b

Se reconstruyeron desde los textos los cuatro campos de los 36 casos, antes de comparar esa lectura con `expected`: **144 valores comparados y cero discrepancias de etiqueta**. Se inspeccionaron en contexto las 113 citas no nulas. Esta revisión fue asistida por Codex y no equivale a una confirmación humana independiente. El [registro detallado](benchmark-v1-review.md) describe el método, los casos y las decisiones.

Dos frases se corrigieron por naturalidad en `bench-014` y `bench-033`; se mantuvieron todos los valores esperados y la partición. La cita de Docker de `bench-014` se ajustó al texto nuevo. El borrador pasó a `benchmark-v1-draft-0.1.1`, actualizado el `2026-10-10T22:02:58Z`, con hash LF `b4ee52f0c16ea937a87c112540a37d2ca5424c6792c9a2e1cdd88856c35e8b0d` en el manifiesto. Los 36 estados siguen en `draft` y no se ejecutó ningún modelo sobre ellos.

La segunda lectura asistida se realizó para siete casos no modificados de la muestra predefinida de nueve, más de 43 horas después de la creación. Resultaron concordantes. Para los dos casos corregidos se reinicia el plazo: `bench-014` y `bench-033` solo pueden releerse desde **2026-10-11T22:02:58Z**, equivalente al 11 de octubre a las 19:02 en America/Santiago. La revisión diferida está **7/9**, por lo que aún no se declara completa.

Verificación de esta entrega: `evalia validate` aceptó 36 casos, el comprobador del benchmark confirmó hash, partición y 24 casos con alguna ausencia o valor no determinable, y la suite completa aprobó **126 pruebas**. Ruff lint, formato del script modificado y `git diff --check` pasaron. Estas comprobaciones mecánicas no sustituyen la revisión semántica humana. No hubo llamadas pagadas ni ejecuciones de modelos sobre el benchmark.

La subtarea **5.2 sigue abierta**. El siguiente trabajo es releer esos dos textos después del plazo, registrar cualquier nueva corrección, obtener la comprobación y confirmación humana de los 36 casos y entonces actualizar estados, versión y hash y congelar el contenido final de `test`. No se requiere configuración nueva por parte de la persona usuaria.

## 10 de octubre de 2026 — corrección de hallazgos de revisión

Se corrigieron dos fallos reproducidos durante la revisión del código. La línea base 0.1.1 clasifica cada habilidad según la señal obligatoria, deseable o negada pertinente dentro de una cláusula mixta; las pruebas cubren ambos órdenes, negaciones y listas de dos habilidades obligatorias. El comando `evalia run` devuelve un mensaje específico y código 2 cuando `--output` ya existe, y conserva intacto el directorio previo. La consulta de documentación de Typer mediante Context7 confirmó el uso de `typer.Exit` con código distinto de cero para errores esperados.

El reporte versionado de la línea base se regeneró por el cambio de versión y hash del código. Las predicciones y métricas de los nueve casos puntuados del conjunto `seed` permanecieron idénticas. La PR #7 se cerró sin integrar: después de resolver conflictos tenía cero archivos distintos de `main`, donde el trabajo de `seed` ya estaba presente. La suite completa aprobó **135 pruebas**; Ruff lint y formato de los archivos Python modificados, el comprobador `--check` del reporte y `git diff --check` se ejecutaron para esta entrega. No se usaron modelos ni proveedores pagados sobre el benchmark ampliado.

La subtarea **5.2 permanece abierta** en 7/9 lecturas diferidas. Lo siguiente es releer `bench-014` y `bench-033` desde el 11 de octubre a las 19:02 en America/Santiago y obtener la confirmación humana de los 36 casos. No se requiere configuración nueva para continuar.

## 11 de octubre de 2026 — segunda lectura asistida completa de 5.2.b

Transcurrido el plazo de los dos textos corregidos, se releyeron `bench-014` y `bench-033` desde `text` antes de consultar `expected`. La lectura concluyó a las `2026-10-11T22:37:50Z`, más de 24 horas después de la corrección. `bench-014` mantiene cierre `2027-12-03`, modalidad desconocida, Docker obligatorio y negación explícita del requisito de estudiante; sus tres citas respaldan esos valores. `bench-033` mantiene los cuatro campos ausentes o no determinables: no informa cierre, ofrece modalidades alternativas sin fijar una, Docker es deseable y mencionar personas jóvenes no prueba que deban ser estudiantes. No se detectaron discrepancias ni se cambió el conjunto.

La muestra de segunda lectura **asistida** queda **9/9**. Se preparó una [hoja de revisión humana](benchmark-v1-human-review.md) que enlaza los 36 casos de la versión `benchmark-v1-draft-0.1.1` y su hash `b4ee52f0c16ea937a87c112540a37d2ca5424c6792c9a2e1cdd88856c35e8b0d`, sin duplicar sus respuestas esperadas. El esquema y el JSONL siguen siendo las fuentes autoritativas. `evalia validate` aceptó 36 casos y `check_benchmark_v1.py` comprobó partición, estados y hash; la documentación pasó `git diff --check`. No se ejecutaron modelos ni se usaron proveedores pagados.

La **5.2 sigue abierta**: la persona responsable debe comprobar las etiquetas, citas, procedencia y permiso de publicación de los 36 casos y comunicar discrepancias o una confirmación explícita referida a ese hash. Hasta entonces todos siguen en `draft`, no se congela el contenido final de `test` y no se comparan modelos. No hace falta configurar servicios ni instalar herramientas para realizar esa revisión.

## 11 de octubre de 2026 — cierre de la subtarea 5.2

La persona responsable confirmó explícitamente como conformes los 36 casos de `benchmark-v1-draft-0.1.1`, identificados por el hash LF `b4ee52f0c16ea937a87c112540a37d2ca5424c6792c9a2e1cdd88856c35e8b0d`; no comunicó discrepancias. Antes del cambio se comprobó que el JSONL conservaba exactamente ese hash y los 36 casos seguían en `draft`. Esta confirmación humana comunicada se distingue de la validación mecánica y de las nueve segundas lecturas asistidas.

Los 36 casos cambiaron únicamente `review_status` a `reviewed`; una comparación de objetos con la versión borrador, excluido ese campo, no encontró cambios en textos, etiquetas, citas, partición ni procedencia. El manifiesto pasó a `benchmark-v1-1.0.0`, `phase=reviewed`, actualizado el `2026-10-11T22:47:52Z`. El hash LF global es `598740b54573749e6c7eb9007117f39d9fc971c7a1ee93550a44243d22c0926c` y el hash LF de los nueve casos `test` es `86dca1777e7b3dbb4dd523d3204f797f2ed5b2f6b42d4cb7d92334ec87b40e34`. El comprobador exige ahora esta segunda huella en fase `reviewed` y detecta cambios de `test` aunque se actualice el hash global. La referencia final permanece sintética; aún no hay métricas comparativas de modelos.

Verificación de cierre: `evalia validate` aceptó los 36 casos; el comprobador del benchmark confirmó la partición 27 `dev` / 9 `test`, cobertura, estados y hashes. Tres pruebas nuevas ejercitan el manifiesto revisado y la detección de una modificación de `test`; la suite completa pasó con **138 pruebas**. Ruff pasó después de aplicar su formato, al igual que `git diff --check`. No se ejecutaron modelos ni se usaron proveedores pagados. La siguiente subtarea prevista dentro del paso 5 es **5.3, comparación local controlada de dos configuraciones**; no se ejecutó aquí. Para cerrar 5.2 no se necesita configuración adicional por parte de la persona usuaria.

## 11 de octubre de 2026 — revisión de optimización y seguridad del código actual

Se contrastaron nueve propuestas con las llamadas reales, el límite actual de 100 casos por ejecución y el plan. En esta entrega se aplica **solo la optimización 2.1**: `case_validator()` y `_definition_validator()` reutilizan instancias por proceso con `functools.cache`, como ya hace `runner/schema.py`. `validate_jsonl_lines` construía un validador una vez por archivo, no una vez por línea; la repetición sí ocurría en `grade_case` y al validar evidencia durante `evaluate_dataset`. El esquema JSON sigue siendo la única fuente autoritativa. Una edición del esquema en una instalación editable requiere reiniciar el proceso para renovar esta caché. No se declara una mejora porcentual sin medirla en una carga representativa.

Decisiones sobre las demás propuestas:

- **2.2, persistencia:** `fsync` por registro y reemplazo atómico del manifiesto son decisiones de durabilidad. El archivo temporal se cierra antes de `os.replace`. No hay un fallo `WinError 32` reproducido ni una medición de cuello de botella que justifique reducir esas garantías; si aparece, se añadirá una prueba de fallo transitorio y un reintento acotado solo al reemplazo.
- **2.3, streaming:** `load_reviewed_cases` conserva los bytes exactos para su hash y valida el conjunto completo antes de crear la salida; el límite actual es 100 casos. Se reconsiderará una pasada incremental que preserve ambas propiedades al ampliar el tamaño permitido, sin afirmar que hoy sea un problema de memoria.
- **2.4, concurrencia:** el motor registra cada solicitud secuencialmente para conservar orden, reintentos y trazabilidad. No existe una medición que respalde tiempos de 20–30 segundos con varios trabajadores. Se evaluará después de la comparación local y antes de usar un proveedor remoto con presupuesto.
- **3.1, puerto Ollama:** el CLI acepta puertos alternativos, pero limita la URL a HTTP de loopback, sin credenciales ni rutas, y no expone esa entrada a una web. El panel local futuro exigirá aceptación explícita antes de usar un puerto personalizado; la demo pública no tendrá acceso al proveedor.
- **3.2, rutas:** el CLI local permite archivos elegidos por su operador; restringirlo a la raíz del repositorio rompería ese uso. El panel local futuro resolverá y contendrá las rutas que reciba de la interfaz en directorios permitidos. La demo pública leerá solo exportaciones preseleccionadas.
- **3.3, separación de interfaces:** el plan ahora identifica `app/public_app.py` y `app/local_app.py` como puntos de entrada distintos. El público no importará proveedor ni motor. Aún no hay aplicaciones web implementadas.
- **3.4, OpenRouter:** no hay adaptador ni clave remota en esta versión. Antes del paso 9 se comprobarán redacción de errores, estimación previa, límite acumulado y tope de la clave sin reinicio; un corte basado solo en el gasto ya informado no impide exceder el presupuesto en la solicitud siguiente.
- **3.5, exportación:** el paso 6 ya exige lista permitida de campos y una prueba negativa con `redistribution_allowed=false`. No existe aún `export-public`, por lo que no hay exportación actual que filtrar.

Verificación de esta entrega: 138 pruebas aprobadas, Ruff lint y formato correctos y reutilización de los tres validadores comprobada en el mismo proceso. No se cambió el contrato de datos, no se ejecutaron modelos y no se usaron servicios pagados. Sigue **5.3** como próxima subtarea funcional. No se requiere configuración de la persona usuaria para esta optimización.

## 11 de octubre de 2026 — subtarea 5.3.a, protocolo y disponibilidad local

Se fijó el [protocolo previo](local-comparison-protocol.md) antes de ejecutar modelos sobre `benchmark-v1`. La 5.3 se divide en cuatro entregas: **a)** entradas, criterios y disponibilidad; **b)** corrida de `qwen3:8b`; **c)** corrida de `qwen2.5-coder:7b` con el mismo conjunto, prompt y límites; **d)** dos repeticiones adicionales por modelo de una muestra `dev` preseleccionada y auditoría técnica pareada. La puntuación y exportación siguen en el paso 6. No se adaptará el prompt tras observar `test`.

El conjunto revisado sigue en `benchmark-v1-1.0.0` con 36 casos, 27 `dev` y 9 `test`, hash LF global `598740b54573749e6c7eb9007117f39d9fc971c7a1ee93550a44243d22c0926c` y hash LF de `test` `86dca1777e7b3dbb4dd523d3204f797f2ed5b2f6b42d4cb7d92334ec87b40e34`. El prompt `convocatorias-es` 1.0.0 tiene hash SHA-256 de bytes exactos `2535a9c5f6ab590ca356647dc342958a5459f3a2685ab67523db55a9ed37c86e`. La muestra de nueve IDs fijada por estratos pasó una comprobación de `split=dev` y `review_status=reviewed` en todos sus casos. El contrato autoritativo y los artefactos de `runs/` no se modificaron.

El cliente Ollama informa versión `0.32.14` y los manifiestos y blobs de ambos modelos candidatos están presentes localmente; no se descargó ninguno. `ollama list` no pudo conectar con un servidor activo y no se encontró proceso Ollama. La variable de entorno de la sesión es `OLLAMA_HOST=0.0.0.0`, valor que podría hacer que el servidor escuche en interfaces de red si se inicia heredándolo. La documentación oficial de Ollama, consultada mediante Context7, confirma que `OLLAMA_HOST` controla la dirección de escucha. La siguiente subtarea **5.3.b** exige iniciar o verificar el servicio en `127.0.0.1:11434` con un valor de entorno seguro para ese proceso y comprobar nombres y digests mediante `/api/tags` antes de inferir. Si no puede iniciarse desde este entorno, la persona usuaria deberá abrirlo con esa dirección; se avisará antes de ejecutar. En 5.3.a no hubo inferencia, llamadas pagadas ni cambios de configuración permanente.

## 15 de octubre de 2026 — subtarea 5.3.b, primera corrida local

Se inició Ollama 0.32.14 para esta corrida con `OLLAMA_HOST=127.0.0.1:11434` solo en el proceso. Se comprobó que el puerto escuchaba exclusivamente en `127.0.0.1` y que `/api/tags` informaba el modelo exacto `qwen3:8b`, digest `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`. También estaba presente `qwen2.5-coder:7b`, digest `dae161e27b0e90dd1856c8bb3209201fd6736d8eb66298e75ed87571486f4364`, sin ejecutarlo. `/api/ps` no informó modelos cargados antes de la corrida. La GPU informaba NVIDIA GeForce RTX 5060 Ti, 16 311 MiB totales, 15 224 MiB libres y 29 % de utilización en la lectura previa; son condiciones puntuales, no un control del entorno durante cada solicitud.

Antes de inferir, `evalia validate` aceptó 36 casos y `python scripts/check_benchmark_v1.py` comprobó 27 `dev`, 9 `test` y el SHA-256 LF `598740b54573749e6c7eb9007117f39d9fc971c7a1ee93550a44243d22c0926c`. El prompt conservó su SHA-256 de bytes exactos `2535a9c5f6ab590ca356647dc342958a5459f3a2685ab67523db55a9ed37c86e`. El archivo JSONL en este checkout tiene saltos CRLF, por lo que su SHA-256 de bytes exactos, registrado por el motor en el manifiesto, es `55641ff55409d3951c88a337635ccbb6a131f1f632d9efab50c96961df75536f`. No se cambiaron casos, prompt ni parámetros para esta corrida.

`evalia run` procesó secuencialmente las 36 líneas con temperatura `0`, límite de `256` tokens, tiempo de espera `120` segundos y `0` reintentos. La salida privada está en `runs/5-3-b-qwen3-20261015/`, excluida por `.gitignore`, con `manifest.json` y `responses.jsonl`. El manifiesto declara `source_commit=4a723e158072191f87250f46cec3123f836e741d`, estado `completed`, 36 solicitudes, 36 registros, 36 éxitos de proveedor y cero errores. Una auditoría posterior validó el manifiesto y los 36 registros contra el esquema de ejecuciones, cotejó los 36 IDs en orden, los 36 hashes de solicitud, el digest, el prompt y el commit, y confirmó un intento por caso sin errores registrados. Las 36 respuestas crudas son objetos JSON parseables; esta comprobación es solo sintáctica, no de contrato de extracción ni de calidad. El primer caso tardó 7109 ms y la mediana de los otros 35 fue 785 ms; se registraron 6900 tokens de entrada y 1443 de salida. Son datos de esta única corrida local, sin inferencia de rendimiento general.

La **5.3.b queda completa** como ejecución y auditoría técnica de una configuración. No se calcularon puntuaciones, no se publicaron respuestas crudas y no hubo llamadas pagadas. El proceso temporal de Ollama se cerró al terminar; no se modificó la configuración permanente. La siguiente subtarea es **5.3.c**, ejecutar `qwen2.5-coder:7b` con el mismo conjunto, prompt y límites. Antes de iniciarla se volverán a comprobar escucha en loopback, nombres y digests de `/api/tags`, hashes de entrada y disponibilidad del equipo.
