# Revisión asistida del benchmark v1

## Estado de la revisión

La revisión semántica asistida de los 36 borradores se realizó el **10 de octubre de 2026**. Se reconstruyeron los cuatro campos de cada texto antes de consultar `expected` en esa pasada: **144 valores comparados, sin discrepancias de etiqueta**. También se examinaron las citas de los valores no nulos para comprobar obligatoriedad, negación, fecha de cierre y modalidad, además de su coincidencia literal validada por `evalia validate`. Esta lectura fue realizada por Codex, que también preparó el borrador inicial; **no sustituye una revisión humana independiente**.

El esquema autoritativo sigue siendo [evalia-case.schema.json](../schemas/evalia-case.schema.json). La partición de 27 `dev` y 9 `test` y sus IDs no cambiaron. No se ejecutaron modelos sobre el conjunto durante la revisión. La muestra de segunda lectura asistida se completó el 11 de octubre (**9/9**). Después, la persona responsable confirmó como conformes los 36 casos de la instantánea indicada en la [hoja de revisión humana](benchmark-v1-human-review.md); todos están ahora en `reviewed`.

## Método y decisiones

1. Se comprobó que el borrador inicial correspondía al hash LF `aac3b05a1b67ada1a9db66d703c00ee6df60a91cd9bb8865eef8954f863aad34` registrado en la entrega 5.2.a, antes de editarlo. La revisión comenzó después del plazo mínimo indicado en el plan.
2. Se leyeron los 36 textos sin mostrar sus `expected`, se reconstruyeron fecha, modalidad, lista de habilidades obligatorias y requisito de estudiante y se compararon los 144 valores con las anotaciones. No hubo diferencias de valor.
3. Se examinaron las 113 citas del borrador y los campos `null` o `[]` en contexto. Las citas de las habilidades afirmadas incluyen la obligatoriedad; las de `student_required=false` incluyen la negación. Las fechas de publicación, entrevista e inicio no se tomaron como cierre, y las ampliaciones explícitas usan el nuevo plazo. La coincidencia literal y los índices Unicode volvieron a pasar el validador.
4. Se detectaron dos frases poco naturales. Se corrigieron de forma editorial, sin cambiar `expected` ni `split`, y se recalcularon las posiciones de evidencia afectadas. La instantánea borrador presentada para confirmación fue `benchmark-v1-draft-0.1.1`, con hash LF `b4ee52f0c16ea937a87c112540a37d2ca5424c6792c9a2e1cdd88856c35e8b0d`.

| Caso | Cambio editorial | Efecto en la referencia |
| --- | --- | --- |
| `bench-014` | «Es obligatorio Docker» → «Docker es obligatorio». | Mantiene `skills=["Docker"]`; cita y posiciones actualizadas. |
| `bench-033` | «No se publicó cierre» → «No se informa fecha de cierre». | Mantiene los cuatro valores ausentes o no determinables; no había citas que desplazar. |

La corrección se registró el **2026-10-10T22:02:58Z** (10 de octubre a las 19:02 en America/Santiago). La segunda lectura de estos dos casos no debe realizarse antes de **2026-10-11T22:02:58Z** (11 de octubre a las 19:02 en America/Santiago).

## Muestra de segunda lectura

El 10 de octubre a las **22:03 UTC** se volvió a leer, más de 43 horas después de la anotación inicial, siete casos de la muestra fijada. En cada uno se reconstruyeron los campos desde el texto y se revisaron las citas correspondientes.

| Caso | Foco de segunda lectura | Resultado asistido |
| --- | --- | --- |
| `bench-001` | Cierre completo, dos habilidades obligatorias y estudiante `true`. | Concordante; las citas respaldan los cuatro campos. |
| `bench-006` | Plazo sin año y ausencia de requisito de estudiante. | Concordante; fecha y estudiante siguen `null`. |
| `bench-011` | Fecha de entrevista frente a cierre. | Concordante; la entrevista no se anotó como cierre. |
| `bench-017` | Python y SQL recomendados. | Concordante; `skills=[]` conserva solo lo obligatorio. |
| `bench-022` | Negación expresa de condición de estudiante. | Concordante; `false` se distingue de `null`. |
| `bench-027` | Corrección del plazo inicial. | Concordante; la cita del nuevo cierre incluye la corrección. |
| `bench-029` | Texto multilínea con emojis. | Concordante; valores y rangos Unicode siguen válidos. |

Al registrar esta primera tanda, `bench-014` y `bench-033` quedaron pendientes por la corrección editorial del 10 de octubre. La sección siguiente registra su lectura posterior al plazo. Si aparece otra corrección, deberá registrarse una nueva versión, hash y plazo del caso afectado.

## 11 de octubre de 2026 — cierre de la segunda lectura asistida

La lectura de los dos textos corregidos concluyó a las **2026-10-11T22:37:50Z** (19:37:50 en America/Santiago), más de 24 horas después de la corrección registrada a las `2026-10-10T22:02:58Z`. Se leyó primero cada `text` sin consultar `expected`; luego se contrastaron las etiquetas y citas del JSONL actual.

| Caso | Reconstrucción desde el texto corregido | Contraste de etiquetas y citas |
| --- | --- | --- |
| `bench-014` | Cierre `2027-12-03`; modalidad `null` porque horario flexible y oficina de contacto no fijan modalidad; `skills=["Docker"]` por «Docker es obligatorio»; estudiante `false` por negación expresa. | Concordante. Las tres citas incluyen el cierre, la obligatoriedad de Docker y la negación sobre estudiantes; sus rangos siguen dentro del texto. |
| `bench-033` | Cierre `null` porque no se informa; modalidad `null` porque remota y presencial son alternativas sin elección; `skills=[]` porque Docker es deseable; estudiante `null` porque dirigirse a jóvenes no exige estar estudiando. | Concordante. Los cuatro campos sin valor no tienen citas; no se infirió una negativa explícita. |

La muestra diferida asistida queda **9/9**, sin nuevas correcciones. El contenido y el hash `b4ee52f0c16ea937a87c112540a37d2ca5424c6792c9a2e1cdd88856c35e8b0d` no cambian. Esta comprobación de Codex no constituye la confirmación humana de los 36 casos.

## 11 de octubre de 2026 — confirmación humana y cierre de 5.2

Ante la solicitud de confirmar o señalar discrepancias en los 36 casos de `benchmark-v1-draft-0.1.1`, identificados por el hash LF `b4ee52f0c16ea937a87c112540a37d2ca5424c6792c9a2e1cdd88856c35e8b0d`, la persona responsable respondió que los confirma como conformes. Este registro documenta su confirmación comunicada; no atribuye a Codex una segunda revisión humana independiente. No se comunicaron IDs ni campos para corregir.

Tras comprobar que el hash y los 36 estados `draft` coincidían con la instantánea confirmada, se cambió únicamente `review_status` a `reviewed`. La comparación de cada objeto antes y después, excluido ese campo, no encontró cambios en textos, etiquetas, citas, `split` ni procedencia. La versión `benchmark-v1-1.0.0`, actualizada el `2026-10-11T22:47:52Z`, tiene hash LF global `598740b54573749e6c7eb9007117f39d9fc971c7a1ee93550a44243d22c0926c` y hash LF de los nueve registros `test` `86dca1777e7b3dbb4dd523d3204f797f2ed5b2f6b42d4cb7d92334ec87b40e34`. El [manifiesto](../datasets/benchmark-v1-manifest.json) conserva ambas huellas y los IDs de prueba. El validador y el comprobador mecánico vuelven a ejecutarse sobre el estado final; sus resultados están en la [bitácora](progress.md).

La comparación de modelos o prompts corresponde a la siguiente subtarea. Si se modifica la referencia, se documentará una nueva versión y la revisión humana de los casos afectados; actualizar un hash por sí solo no renueva la conformidad semántica.
