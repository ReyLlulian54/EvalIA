# Revisión de publicación — 6.e

Estado: **revisión humana y selección completadas el 17 de octubre de 2026 (America/Santiago)**. Esta guía acompaña el [protocolo fijado antes de puntuar](comparison-protocol.md); no cambia la muestra ni la rúbrica. La hoja confirmada, la prelectura y la decisión están bajo `work/`, excluidas de Git. No copiar su contenido a una PR.

## 1. Revisión de respaldo semántico

Revisar los diez IDs preseleccionados: `bench-002`, `bench-008`, `bench-014`, `bench-021`, `bench-028`, `bench-035` (`dev`) y `bench-001`, `bench-011`, `bench-017`, `bench-027` (`test`). Para **cada uno de los cuatro campos de cada modelo**, leer el texto antes de juzgar la predicción. Registrar en la hoja `respaldo_claro`, `sin_respaldo` o `ambiguo`, y explicar el tramo del texto que fundamenta la decisión o la duda. Son 80 juicios. Una coincidencia con la etiqueta esperada o una cita literal no demuestra por sí sola respaldo semántico. `false` requiere una negación explícita; `null` significa que el texto no permite determinar el valor. Si una respuesta tiene error de formato, conservarlo y juzgar sus valores crudos solo como observación cualitativa, sin cambiar los resultados automáticos.

La hoja privada coteja los hashes de bytes de las dos corridas con sus informes y los informes con la comparación. La prelectura asistida está separada de `work/6-e-human-review-confirmed.md`, que registra la confirmación explícita de la persona responsable. Registrar casos adicionales discrepantes por separado, sin sustituir los diez fijados.

## 2. Derechos de los casos seleccionables

Antes de generar la exportación, revisar cada caso que se quiera publicar. La hoja incluye los 36 IDs del benchmark y sus metadatos declarados. El [registro de creación](benchmark-v1.md) afirma que son textos ficticios originales para EvalIA, pero `redistribution_allowed=true` y `LicenseRef-EvalIA-Original` no constituyen autorización por sí solos. Confirmar titularidad o permiso, alcance de publicación de etiquetas y predicciones, y registrar evidencia y responsable. Si un caso no queda autorizado, excluirlo de la selección o detener la publicación.

Con la revisión completada, crear el registro privado `work/6-d-permission-review.json` conforme al [contrato de permisos](../schemas/evalia-publication-approval.schema.json), con una entrada por cada caso seleccionado, los SHA-256 de bytes exactos, fecha, persona y referencia de evidencia. La guía de [exportación segura](export-public.md) contiene el comando. El registro y la hoja permanecen en `work/`.

## 3. Auditoría del candidato y decisión

Ejecutar `evalia export-public` solo después del registro de permisos. Validar el JSON generado contra el [contrato público](../schemas/evalia-public-report.schema.json) con Draft 2020-12 y comprobación de formato. Revisar manualmente la raíz, procedencia, limitaciones, agregados `dev`/`test` y **cada caso y campo** del candidato. Confirmar que los IDs seleccionados, etiquetas, predicciones, categorías y errores concuerdan con la comparación privada; que `null` no se convirtió en `false`; que no hay texto de entrada, citas, prompt, `raw_text`, rutas locales, secretos ni registro de permisos. Conservar el SHA-256 del candidato y el resultado de la revisión.

El contrato público 0.1.1 distingue `pending_artifact_review` del estado `approved_for_publication`. El exportador siempre genera el primero en privado. Solo después de la revisión humana, los permisos y la auditoría del JSON se selecciona una copia idéntica salvo por ese estado; su esquema se valida de nuevo. La demo corresponde al paso 8.

## Resultado registrado

La persona responsable confirmó los 80 juicios de los diez casos fijados: 76 con respaldo claro y cuatro sin respaldo; no hubo juicios ambiguos. Los cuatro sin respaldo corresponden a la candidata: habilidades y requisito de estudiante en `bench-008`, requisito de estudiante en `bench-011` y habilidades en `bench-017`. En `bench-001` y `bench-035`, ambos modelos escribieron `Python 3`: la mención existe en el texto, pero el contrato exige `Python`, de modo que el error de formato automático se conserva. La persona responsable también confirmó la creación original y los derechos de publicación de los 36 casos.

El candidato privado 0.1.1 tiene SHA-256 `67e92fb22a0652a60e83257da5625132ec5e05e3005be61133b76b46ce84973d`. La auditoría cotejó los 36 casos, campos, errores, tiempos, categorías y agregados con las fuentes congeladas; validó el esquema con formatos y no encontró textos, prompt, respuestas crudas, rutas ni datos del registro de permisos. La decisión privada vincula la hoja humana, los permisos, la auditoría y los hashes.

Se seleccionó [el reporte estructurado](../examples/results/benchmark-v1-qwen3-vs-qwen25.json), SHA-256 de bytes LF `7071ee504391a38c9866342481ff5124bdd75199c74189b17e024baf32f22565`, para la demo de solo lectura. `.gitattributes` fija LF en ese archivo para conservar la huella entre plataformas. Su `publication_review` es `approved_for_publication`; el único cambio respecto del candidato auditado es ese estado. Son 36 casos ficticios (27 `dev`, 9 `test`), sin citas de los modelos ni ganador declarado. El archivo no incluye los textos de entrada ni las respuestas crudas. La demo web aún corresponde al paso 8.
