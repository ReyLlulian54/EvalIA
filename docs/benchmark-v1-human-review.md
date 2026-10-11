# Hoja de revisión humana — benchmark v1

Instantánea: `benchmark-v1-draft-0.1.1`; SHA-256 del JSONL normalizado a LF: `b4ee52f0c16ea937a87c112540a37d2ca5424c6792c9a2e1cdd88856c35e8b0d`.

Esta hoja ayuda a navegar el conjunto. El [JSONL](../datasets/benchmark-v1.jsonl) y el [esquema](../schemas/evalia-case.schema.json) son las fuentes autoritativas. Ninguna fila está aprobada todavía. Si cambia el hash, esta hoja debe revisarse de nuevo.

## Cómo revisar

1. Abre cada caso enlazado y lee primero `text`, sin usar `expected` como pista. Reconstruye fecha de cierre, modalidad, habilidades técnicas obligatorias y requisito explícito de ser estudiante según la [guía](annotation-guide.md).
2. Compara tu lectura con `expected`. Distingue `null` de `false` y `[]` de una lista de habilidades. Comprueba también `split`, procedencia y permiso de redistribución.
3. Para cada valor no nulo, lee la cita de `evidence` en su contexto y comprueba que respalda semánticamente la etiqueta; la validación automática solo comprueba literalidad e índices.
4. Si encuentras una discrepancia, comunica el ID, campo y motivo. Corregiremos el caso, renovaremos versión/hash y repetiremos la revisión diferida del caso modificado antes de aprobarlo.
5. Cuando hayas revisado los 36, confirma explícitamente si el conjunto con el SHA-256 indicado es conforme o señala los casos pendientes. Hasta entonces todos siguen en `draft` y no se ejecutan modelos sobre `test`.

## Casos por revisar

| Caso y línea del JSONL | Partición | Revisión humana |
| --- | --- | --- |
| [`bench-001`](../datasets/benchmark-v1.jsonl#L1) · línea 1 | `test` | Pendiente |
| [`bench-002`](../datasets/benchmark-v1.jsonl#L2) · línea 2 | `dev` | Pendiente |
| [`bench-003`](../datasets/benchmark-v1.jsonl#L3) · línea 3 | `dev` | Pendiente |
| [`bench-004`](../datasets/benchmark-v1.jsonl#L4) · línea 4 | `dev` | Pendiente |
| [`bench-005`](../datasets/benchmark-v1.jsonl#L5) · línea 5 | `dev` | Pendiente |
| [`bench-006`](../datasets/benchmark-v1.jsonl#L6) · línea 6 | `dev` | Pendiente |
| [`bench-007`](../datasets/benchmark-v1.jsonl#L7) · línea 7 | `test` | Pendiente |
| [`bench-008`](../datasets/benchmark-v1.jsonl#L8) · línea 8 | `dev` | Pendiente |
| [`bench-009`](../datasets/benchmark-v1.jsonl#L9) · línea 9 | `dev` | Pendiente |
| [`bench-010`](../datasets/benchmark-v1.jsonl#L10) · línea 10 | `dev` | Pendiente |
| [`bench-011`](../datasets/benchmark-v1.jsonl#L11) · línea 11 | `test` | Pendiente |
| [`bench-012`](../datasets/benchmark-v1.jsonl#L12) · línea 12 | `dev` | Pendiente |
| [`bench-013`](../datasets/benchmark-v1.jsonl#L13) · línea 13 | `dev` | Pendiente |
| [`bench-014`](../datasets/benchmark-v1.jsonl#L14) · línea 14 | `dev` | Pendiente |
| [`bench-015`](../datasets/benchmark-v1.jsonl#L15) · línea 15 | `test` | Pendiente |
| [`bench-016`](../datasets/benchmark-v1.jsonl#L16) · línea 16 | `dev` | Pendiente |
| [`bench-017`](../datasets/benchmark-v1.jsonl#L17) · línea 17 | `test` | Pendiente |
| [`bench-018`](../datasets/benchmark-v1.jsonl#L18) · línea 18 | `dev` | Pendiente |
| [`bench-019`](../datasets/benchmark-v1.jsonl#L19) · línea 19 | `dev` | Pendiente |
| [`bench-020`](../datasets/benchmark-v1.jsonl#L20) · línea 20 | `dev` | Pendiente |
| [`bench-021`](../datasets/benchmark-v1.jsonl#L21) · línea 21 | `dev` | Pendiente |
| [`bench-022`](../datasets/benchmark-v1.jsonl#L22) · línea 22 | `test` | Pendiente |
| [`bench-023`](../datasets/benchmark-v1.jsonl#L23) · línea 23 | `dev` | Pendiente |
| [`bench-024`](../datasets/benchmark-v1.jsonl#L24) · línea 24 | `dev` | Pendiente |
| [`bench-025`](../datasets/benchmark-v1.jsonl#L25) · línea 25 | `dev` | Pendiente |
| [`bench-026`](../datasets/benchmark-v1.jsonl#L26) · línea 26 | `dev` | Pendiente |
| [`bench-027`](../datasets/benchmark-v1.jsonl#L27) · línea 27 | `test` | Pendiente |
| [`bench-028`](../datasets/benchmark-v1.jsonl#L28) · línea 28 | `dev` | Pendiente |
| [`bench-029`](../datasets/benchmark-v1.jsonl#L29) · línea 29 | `dev` | Pendiente |
| [`bench-030`](../datasets/benchmark-v1.jsonl#L30) · línea 30 | `dev` | Pendiente |
| [`bench-031`](../datasets/benchmark-v1.jsonl#L31) · línea 31 | `test` | Pendiente |
| [`bench-032`](../datasets/benchmark-v1.jsonl#L32) · línea 32 | `dev` | Pendiente |
| [`bench-033`](../datasets/benchmark-v1.jsonl#L33) · línea 33 | `test` | Pendiente |
| [`bench-034`](../datasets/benchmark-v1.jsonl#L34) · línea 34 | `dev` | Pendiente |
| [`bench-035`](../datasets/benchmark-v1.jsonl#L35) · línea 35 | `dev` | Pendiente |
| [`bench-036`](../datasets/benchmark-v1.jsonl#L36) · línea 36 | `dev` | Pendiente |

La segunda lectura asistida de la muestra de nueve casos está documentada en el [registro](benchmark-v1-review.md); no reemplaza la revisión humana de las 36 filas.
