# Revisión de publicación — 6.e

Estado: **pendiente de confirmación humana**. Esta guía acompaña el [protocolo fijado antes de puntuar](comparison-protocol.md); no cambia la muestra ni la rúbrica. La hoja con textos, respuestas y casillas está en `work/6-e-human-review.md`, excluida de Git. No copiar su contenido a una PR.

## 1. Revisión de respaldo semántico

Revisar los diez IDs preseleccionados: `bench-002`, `bench-008`, `bench-014`, `bench-021`, `bench-028`, `bench-035` (`dev`) y `bench-001`, `bench-011`, `bench-017`, `bench-027` (`test`). Para **cada uno de los cuatro campos de cada modelo**, leer el texto antes de juzgar la predicción. Registrar en la hoja `respaldo_claro`, `sin_respaldo` o `ambiguo`, y explicar el tramo del texto que fundamenta la decisión o la duda. Son 80 juicios. Una coincidencia con la etiqueta esperada o una cita literal no demuestra por sí sola respaldo semántico. `false` requiere una negación explícita; `null` significa que el texto no permite determinar el valor. Si una respuesta tiene error de formato, conservarlo y juzgar sus valores crudos solo como observación cualitativa, sin cambiar los resultados automáticos.

La hoja privada coteja los hashes de bytes de las dos corridas con sus informes y los informes con la comparación. Es una preparación asistida; la persona responsable debe completar y fechar los juicios. Registrar casos adicionales discrepantes por separado, sin sustituir los diez fijados.

## 2. Derechos de los casos seleccionables

Antes de generar la exportación, revisar cada caso que se quiera publicar. La hoja incluye los 36 IDs del benchmark y sus metadatos declarados. El [registro de creación](benchmark-v1.md) afirma que son textos ficticios originales para EvalIA, pero `redistribution_allowed=true` y `LicenseRef-EvalIA-Original` no constituyen autorización por sí solos. Confirmar titularidad o permiso, alcance de publicación de etiquetas y predicciones, y registrar evidencia y responsable. Si un caso no queda autorizado, excluirlo de la selección o detener la publicación.

Con la revisión completada, crear el registro privado `work/6-d-permission-review.json` conforme al [contrato de permisos](../schemas/evalia-publication-approval.schema.json), con una entrada por cada caso seleccionado, los SHA-256 de bytes exactos, fecha, persona y referencia de evidencia. La guía de [exportación segura](export-public.md) contiene el comando. El registro y la hoja permanecen en `work/`.

## 3. Auditoría del candidato y decisión

Ejecutar `evalia export-public` solo después del registro de permisos. Validar el JSON generado contra el [contrato público](../schemas/evalia-public-report.schema.json) con Draft 2020-12 y comprobación de formato. Revisar manualmente la raíz, procedencia, limitaciones, agregados `dev`/`test` y **cada caso y campo** del candidato. Confirmar que los IDs seleccionados, etiquetas, predicciones, categorías y errores concuerdan con la comparación privada; que `null` no se convirtió en `false`; que no hay texto de entrada, citas, prompt, `raw_text`, rutas locales, secretos ni registro de permisos. Conservar el SHA-256 del candidato y el resultado de la revisión.

El contrato 0.1.0 marca el archivo generado como `pending_artifact_review`. Esa marca describe al candidato privado; no equivale a aprobación. Tras la revisión, documentar qué archivo y hash se selecciona para la demo de solo lectura y cómo se representa su aprobación en el contrato antes de incorporarlo a `examples/results/`. La demo corresponde al paso 8. No declarar 6.e completa ni publicar un artefacto hasta cerrar todos estos puntos.
