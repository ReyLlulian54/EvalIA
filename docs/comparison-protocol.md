# Protocolo de comparación y exportación — etapa 6

Estado: **fijado en 6.a antes de puntuar las corridas principales**. Esta entrega define el método y las puertas de las subtareas. No contiene puntuaciones ni respuestas de modelos. Los contratos de entrada siguen siendo [`evalia-case.schema.json`](../schemas/evalia-case.schema.json) y [`evalia-run.schema.json`](../schemas/evalia-run.schema.json); la [rúbrica](scoring.md) define los conteos. Cada contrato nuevo de salida se creará como JSON Schema versionado antes de implementar su productor.

## Subtareas y puertas

| Subtarea | Entrega verificable | Puerta para continuar |
| --- | --- | --- |
| **6.a. Método y puertas** | Fijar corridas, compatibilidad, reglas de puntuación, muestra de revisión humana y límites de publicación. | Confirmar que las entradas, el prompt y los artefactos privados siguen disponibles y que el método no usa salidas de `test` para cambiar la rúbrica. |
| **6.b. Puntuación privada por corrida** | Crear `schemas/evalia-score-report.schema.json` antes de adaptar registros del motor a los evaluadores existentes. Conservar errores de proveedor y de formato, y separar `dev` y `test`. | Pruebas con respuestas simuladas para JSON inválido, claves duplicadas, tipos incorrectos, `null`/`false`, habilidades no canónicas y denominador cero; después puntuar las dos corridas congeladas. |
| **6.c. Comparación pareada** | Crear `schemas/evalia-comparison.schema.json` antes de implementar `evalia compare` y su reporte privado por campo y por caso, con base y candidato explícitos. | Rechazar corridas incompatibles; comprobar por pruebas mejoras, regresiones, empates y casos no comparables, sin puntuación compuesta. |
| **6.d. Exportación segura** | Crear `schemas/evalia-public-report.schema.json` antes de implementar `evalia export-public` mediante lista permitida. | Rechazar casos seleccionados con `redistribution_allowed=false`, campos no permitidos y procedencia no verificable; probar que texto, prompt y respuestas crudas no salgan. |
| **6.e. Revisión y artefacto publicable** | Revisar semánticamente la muestra fijada y el JSON exportado; registrar decisiones y seleccionar el artefacto para la demo de solo lectura. | Revisión humana realizada y documentada, permisos de publicación comprobados, JSON conforme al esquema y sin datos privados. La demo web se implementará en el paso 8. |

Cada fila es una entrega independiente. No se implementan filas posteriores para cerrar una anterior.

## Entradas congeladas para 6.b y 6.c

- Referencia: `datasets/benchmark-v1.jsonl`, versión `benchmark-v1-1.0.0`, 36 casos `reviewed` (27 `dev`, 9 `test`). SHA-256 LF `598740b54573749e6c7eb9007117f39d9fc971c7a1ee93550a44243d22c0926c`; SHA-256 de bytes del checkout usado en 5.3 `55641ff55409d3951c88a337635ccbb6a131f1f632d9efab50c96961df75536f`. El manifiesto del conjunto y el esquema de casos son la autoridad sobre su estructura y revisión.
- Prompt: `prompts/extraction-v1.json`, SHA-256 de bytes `2535a9c5f6ab590ca356647dc342958a5459f3a2685ab67523db55a9ed37c86e`.
- Corrida base: `runs/5-3-b-qwen3-20261015/`, `qwen3:8b`, digest `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`.
- Corrida candidata: `runs/5-3-c-qwen25-20261015/`, `qwen2.5-coder:7b`, digest `dae161e27b0e90dd1856c8bb3209201fd6736d8eb66298e75ed87571486f4364`.
- Las cuatro repeticiones de nueve casos `dev` de 5.3.d sirven para describir estabilidad. No sustituyen las corridas de 36 casos ni amplían el denominador de calidad.

Antes de calcular resultados, validar cada caso y ambos manifiestos y registros con los esquemas existentes. Comprobar que los dos lotes tienen los mismos 36 IDs en el mismo orden, el mismo hash de conjunto y prompt, temperatura `0`, límite `256`, espera `120` segundos y cero reintentos. El hash de solicitud **difiere** entre modelos porque incluye `model_id`; se reconstruirá por modelo. Los commits de origen distintos se conservarán como procedencia, no como incompatibilidad automática. Verificar estado, conteos y errores por registro: `completed` no significa 36 éxitos. Si cambia el gold set, invalidar esta comparación o versionar la referencia y empezar una nueva.

## Puntuación y lectura pareada

La predicción es el objeto JSON crudo de cuatro campos pedido por el prompt. El lector de 6.b rechazará JSON no estándar, claves duplicadas, objetos con claves faltantes o extra, tipos fuera del esquema y habilidades no canónicas. Esos casos se contarán como fallos de formato o de proveedor y no aportarán denominadores de exactitud de contenido. `coverage` tendrá como denominador todos los casos `reviewed` del split correspondiente. La extracción válida se pasará sin corrección posterior a las reglas de [`grade_case`](../src/evalia/graders/core.py) y agregará las mismas métricas de contenido de la [rúbrica](scoring.md): fecha, modalidad, estudiante, habilidades, abstención y sus numeradores y denominadores. `null` y `false` nunca se fusionarán. Con denominador cero, el valor será `null` (no aplicable).

El prompt usado en 5.3 **no solicitó citas**. Por tanto, la métrica automática `evidence_literal` queda **no observada** para estos modelos; no se registrará como cero ni como cita válida. Una respuesta parseable tampoco demuestra corrección. La revisión semántica humana definida abajo examinará respaldo en el texto de la convocatoria y se informará separada de las métricas automáticas.

Cada split (`dev` y `test`) tendrá métricas y errores propios; no se mezclan para escoger un modelo. En 6.c, la dirección se fija como **base → candidata**. Para cada campo de un caso comparable: base incorrecta y candidata correcta es mejora; base correcta y candidata incorrecta es regresión; ambas correctas es empate correcto; ambas incorrectas se informa como empate incorrecto, incluso si cambiaron los valores. Un fallo de proveedor o formato en cualquiera de los lados se muestra como no comparable para ese campo, sin ocultar el fallo de cobertura. Las habilidades tendrán coincidencia exacta y conteos TP/FP/FN separados. No habrá un ganador ni una nota compuesta.

Latencia, tokens y costo informado se mostrarán con cantidad de observaciones y condiciones de captura. La primera solicitud puede incluir carga del modelo y la memoria GPU libre difirió entre corridas; estos datos descriptivos no prueban una diferencia general de eficiencia. El costo de API no informado por Ollama seguirá en `null`, no en cero.

## Revisión humana fijada antes de puntuar

La muestra mínima es de diez casos, elegida por posición dentro de cada split, sin mirar predicciones ni puntajes: posiciones `1, 6, 11, 16, 21, 26` de los 27 `dev` (`bench-002`, `bench-008`, `bench-014`, `bench-021`, `bench-028`, `bench-035`) y posiciones `1, 3, 5, 7` de los nueve `test` (`bench-001`, `bench-011`, `bench-017`, `bench-027`). Una persona revisará los cuatro campos de **cada uno de los dos modelos** para cada caso frente al texto y registrará por campo respaldo claro, falta de respaldo o ambigüedad, más observaciones. Se podrán añadir casos discrepantes después, identificados aparte como revisión dirigida. La selección previa no se reemplazará por casos favorables. Esta revisión está **pendiente**; ninguna validación mecánica la completa.

## Frontera pública

Los informes de puntuación y comparación, manifiestos, textos de entrada, prompts y respuestas crudas permanecerán privados bajo `runs/` o `work/`. El exportador de 6.d construirá un objeto nuevo desde una lista permitida: versión del reporte, identidad y hashes de procedencia publicables, IDs y split, etiquetas y predicciones autorizadas, conteos por campo y por caso, metadatos de modelo y tiempos. No copiará objetos privados completos ni rutas locales, `raw_text`, prompt compuesto, logs o secretos. Todo caso seleccionado deberá estar `reviewed`, tener `redistribution_allowed=true` en el conjunto validado y pasar la revisión de permiso de publicación; ante un caso no autorizado, la exportación fallará cerrada. El indicador por sí solo no concede derechos.

El JSON candidato se validará contra su esquema público y se revisará manualmente antes de incorporarlo a `examples/results/` o a una demo. Los campos y ejemplos públicos deberán cumplir el esquema único de salida, sin redefinirlo en la aplicación. No se ejecutarán modelos ni llamadas pagadas en CI para verificar la etapa 6.
