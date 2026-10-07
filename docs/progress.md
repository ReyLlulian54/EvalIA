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
