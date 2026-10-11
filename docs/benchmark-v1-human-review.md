# Hoja de revisión humana — benchmark v1

Instantánea presentada para confirmación: `benchmark-v1-draft-0.1.1`; SHA-256 del JSONL normalizado a LF: `b4ee52f0c16ea937a87c112540a37d2ca5424c6792c9a2e1cdd88856c35e8b0d`. Referencia resultante tras cambiar solo `review_status`: `benchmark-v1-1.0.0`, hash LF global `598740b54573749e6c7eb9007117f39d9fc971c7a1ee93550a44243d22c0926c`.

Esta hoja ayudó a navegar el conjunto en la revisión y registra la confirmación comunicada por la persona responsable el 11 de octubre de 2026. El [JSONL](../datasets/benchmark-v1.jsonl) y el [esquema](../schemas/evalia-case.schema.json) son las fuentes autoritativas. Si cambia el contenido de algún caso, se requiere revisión de los afectados y actualización de esta hoja.

## Procedimiento usado para revisar

1. Abre cada caso enlazado y lee primero `text`, sin usar `expected` como pista. Reconstruye fecha de cierre, modalidad, habilidades técnicas obligatorias y requisito explícito de ser estudiante según la [guía](annotation-guide.md).
2. Compara tu lectura con `expected`. Distingue `null` de `false` y `[]` de una lista de habilidades. Comprueba también `split`, procedencia y permiso de redistribución.
3. Para cada valor no nulo, lee la cita de `evidence` en su contexto y comprueba que respalda semánticamente la etiqueta; la validación automática solo comprueba literalidad e índices.
4. Si encuentras una discrepancia, comunica el ID, campo y motivo. Corregiremos el caso, renovaremos versión/hash y repetiremos la revisión diferida del caso modificado antes de aprobarlo.
5. Se solicitó confirmar explícitamente la conformidad de los 36 casos con el SHA-256 del borrador indicado o señalar IDs y campos pendientes. La persona responsable confirmó los 36 como conformes, sin comunicar correcciones.

## Casos confirmados

| Caso y línea del JSONL | Partición | Revisión humana |
| --- | --- | --- |
| [`bench-001`](../datasets/benchmark-v1.jsonl#L1) · línea 1 | `test` | Confirmado |
| [`bench-002`](../datasets/benchmark-v1.jsonl#L2) · línea 2 | `dev` | Confirmado |
| [`bench-003`](../datasets/benchmark-v1.jsonl#L3) · línea 3 | `dev` | Confirmado |
| [`bench-004`](../datasets/benchmark-v1.jsonl#L4) · línea 4 | `dev` | Confirmado |
| [`bench-005`](../datasets/benchmark-v1.jsonl#L5) · línea 5 | `dev` | Confirmado |
| [`bench-006`](../datasets/benchmark-v1.jsonl#L6) · línea 6 | `dev` | Confirmado |
| [`bench-007`](../datasets/benchmark-v1.jsonl#L7) · línea 7 | `test` | Confirmado |
| [`bench-008`](../datasets/benchmark-v1.jsonl#L8) · línea 8 | `dev` | Confirmado |
| [`bench-009`](../datasets/benchmark-v1.jsonl#L9) · línea 9 | `dev` | Confirmado |
| [`bench-010`](../datasets/benchmark-v1.jsonl#L10) · línea 10 | `dev` | Confirmado |
| [`bench-011`](../datasets/benchmark-v1.jsonl#L11) · línea 11 | `test` | Confirmado |
| [`bench-012`](../datasets/benchmark-v1.jsonl#L12) · línea 12 | `dev` | Confirmado |
| [`bench-013`](../datasets/benchmark-v1.jsonl#L13) · línea 13 | `dev` | Confirmado |
| [`bench-014`](../datasets/benchmark-v1.jsonl#L14) · línea 14 | `dev` | Confirmado |
| [`bench-015`](../datasets/benchmark-v1.jsonl#L15) · línea 15 | `test` | Confirmado |
| [`bench-016`](../datasets/benchmark-v1.jsonl#L16) · línea 16 | `dev` | Confirmado |
| [`bench-017`](../datasets/benchmark-v1.jsonl#L17) · línea 17 | `test` | Confirmado |
| [`bench-018`](../datasets/benchmark-v1.jsonl#L18) · línea 18 | `dev` | Confirmado |
| [`bench-019`](../datasets/benchmark-v1.jsonl#L19) · línea 19 | `dev` | Confirmado |
| [`bench-020`](../datasets/benchmark-v1.jsonl#L20) · línea 20 | `dev` | Confirmado |
| [`bench-021`](../datasets/benchmark-v1.jsonl#L21) · línea 21 | `dev` | Confirmado |
| [`bench-022`](../datasets/benchmark-v1.jsonl#L22) · línea 22 | `test` | Confirmado |
| [`bench-023`](../datasets/benchmark-v1.jsonl#L23) · línea 23 | `dev` | Confirmado |
| [`bench-024`](../datasets/benchmark-v1.jsonl#L24) · línea 24 | `dev` | Confirmado |
| [`bench-025`](../datasets/benchmark-v1.jsonl#L25) · línea 25 | `dev` | Confirmado |
| [`bench-026`](../datasets/benchmark-v1.jsonl#L26) · línea 26 | `dev` | Confirmado |
| [`bench-027`](../datasets/benchmark-v1.jsonl#L27) · línea 27 | `test` | Confirmado |
| [`bench-028`](../datasets/benchmark-v1.jsonl#L28) · línea 28 | `dev` | Confirmado |
| [`bench-029`](../datasets/benchmark-v1.jsonl#L29) · línea 29 | `dev` | Confirmado |
| [`bench-030`](../datasets/benchmark-v1.jsonl#L30) · línea 30 | `dev` | Confirmado |
| [`bench-031`](../datasets/benchmark-v1.jsonl#L31) · línea 31 | `test` | Confirmado |
| [`bench-032`](../datasets/benchmark-v1.jsonl#L32) · línea 32 | `dev` | Confirmado |
| [`bench-033`](../datasets/benchmark-v1.jsonl#L33) · línea 33 | `test` | Confirmado |
| [`bench-034`](../datasets/benchmark-v1.jsonl#L34) · línea 34 | `dev` | Confirmado |
| [`bench-035`](../datasets/benchmark-v1.jsonl#L35) · línea 35 | `dev` | Confirmado |
| [`bench-036`](../datasets/benchmark-v1.jsonl#L36) · línea 36 | `dev` | Confirmado |

La segunda lectura asistida de la muestra de nueve casos y la confirmación comunicada por la persona responsable se documentan por separado en el [registro](benchmark-v1-review.md).
