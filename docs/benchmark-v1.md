# Benchmark v1 — borrador de casos y revisión pendiente

El archivo [benchmark-v1.jsonl](../datasets/benchmark-v1.jsonl) contiene **36 convocatorias ficticias originales** redactadas para EvalIA, con anotaciones iniciales y evidencia literal. No corresponden a becas, prácticas ni empleos reales. Todos los registros están en `draft`: el conjunto todavía **no es una referencia revisada** ni respalda comparaciones de calidad de modelos.

La estructura de cada línea procede únicamente del [esquema de casos 0.1.0](../schemas/evalia-case.schema.json); la [guía de anotación](annotation-guide.md) define el significado de los campos. El [manifiesto](../datasets/benchmark-v1-manifest.json) fija el hash del borrador y los identificadores de la partición `test`; no duplica las respuestas esperadas.

## Diseño fijado antes de evaluar modelos

- Tamaño: 36 casos, con 27 `dev` y 9 `test` (25 %).
- Partición `test`: `bench-001`, `bench-007`, `bench-011`, `bench-015`, `bench-017`, `bench-022`, `bench-027`, `bench-031` y `bench-033`. Estos IDs se eligieron antes de ejecutar modelos sobre este conjunto y no se usarán para ajustar prompts. Incluyen 3 requisitos de estudiante `true`, 3 `false` y 3 `null`, además de casos sin habilidades obligatorias.
- Procedencia: textos ficticios escritos para el proyecto, `source_url=null` y `source_license=LicenseRef-EvalIA-Original`. No se copiaron anuncios externos. `redistribution_allowed=true` registra su publicación prevista en el repositorio; el identificador no es una licencia estándar.
- Estado: 36 `draft`. La validación del esquema, de citas y de partición no cambia ese estado.
- Cobertura del borrador: 13 fechas `null`, 9 modalidades `null`, 5 listas de habilidades vacías y 11 requisitos de estudiante `null`; los otros requisitos se reparten en 12 `true` y 13 `false`. Hay 24 casos con al menos un campo ausente o no determinable y 113 citas de valores no nulos.

| Estrato | IDs | Caso reservado en `test` | Foco de revisión |
| --- | --- | --- | --- |
| Datos explícitos | 001–004 | 001 | Fecha, modalidad y habilidades obligatorias. |
| Cierre incompleto o ausente | 005–008 | 007 | No inventar año o plazo. |
| Fechas distractoras | 009–012 | 011 | Publicación, entrevista e inicio frente a cierre. |
| Modalidad no fijada | 013–016 | 015 | Alternativas, dirección y horario flexible. |
| Habilidades deseables | 017–020 | 017 | Obligatorio frente a recomendado. |
| Requisito de estudiante | 021–024 | 022 | `true`, `false` explícito y `null`. |
| Actualización del plazo | 025–028 | 027 | Cierre vigente frente a fecha anterior. |
| Unicode y texto adversarial | 029–032 | 031 | Posiciones, título distractor e instrucciones dentro del dato. |
| Combinaciones | 033–036 | 033 | Ausencias, repetición de habilidad y día bisiesto. |

Estas situaciones son deliberadas y sintéticas. La diversidad de redacción y la dificultad pueden diferir de convocatorias reales; la puntuación futura deberá declarar esa limitación.

## Registro de creación e integridad

El borrador con la partición fijada se escribió el **2026-10-09T02:26:36Z** (8 de octubre a las 23:26 en America/Santiago). Hash SHA-256 del JSONL UTF-8 con saltos normalizados a LF: `aac3b05a1b67ada1a9db66d703c00ee6df60a91cd9bb8865eef8954f863aad34`. Se usa la forma LF para que la comprobación sea estable en Windows y otros sistemas; el motor de ejecución, en cambio, registra el hash de los bytes exactos que recibe.

Desde la raíz del repositorio, con el entorno de desarrollo instalado:

```powershell
.\.venv\Scripts\evalia validate datasets\benchmark-v1.jsonl
.\.venv\Scripts\python scripts\check_benchmark_v1.py
```

El primer comando consume el contrato autoritativo y comprueba sintaxis, forma, unicidad, habilidades canónicas y citas literales. El segundo comprueba hash, procedencia, estados, tamaño, cobertura y partición. Ninguno demuestra que una cita respalde semánticamente su etiqueta. Si se corrige un texto o una anotación, registrar motivo y nueva versión, actualizar el hash del manifiesto y volver a validar; no cambiar silenciosamente los IDs de `test`.

## Revisión requerida antes de usar el conjunto

1. **Primera lectura de los 36 casos:** reconstruir fecha, modalidad, habilidades y requisito de estudiante desde cada `text`, sin mirar primero `expected`; comparar después cada valor y su cita. Comprobar en especial que `false` contenga negación explícita, que las habilidades sean obligatorias y que la fecha citada sea el cierre vigente. Registrar correcciones y responsable de la revisión. La creación asistida y la validación mecánica no sustituyen esta lectura humana.
2. **Segunda lectura tras al menos 24 horas:** no empezar antes de **2026-10-10T02:26:36Z** (9 de octubre a las 23:26 en America/Santiago), siempre que el contenido no haya cambiado. Revisar de nuevo al menos 9 casos, uno por estrato: `bench-001`, `bench-006`, `bench-011`, `bench-014`, `bench-017`, `bench-022`, `bench-027`, `bench-029` y `bench-033`. Nueve de 36 equivalen al 25 %, por encima del mínimo del plan de 20 %. Si cambia un caso, contar 24 horas desde su última anotación para su segunda lectura.
3. **Cierre:** documentar por caso cualquier discrepancia y su corrección, confirmar la revisión humana, pasar a `reviewed` solo los casos efectivamente aprobados y crear una versión nueva del conjunto. No ejecutar ni comparar el `test` final hasta congelar el conjunto revisado. El estado `draft` actual permanece mientras falte cualquiera de estas acciones.

La revisión diferida y la confirmación humana **no se han realizado** en esta entrega. El siguiente trabajo es la lectura semántica documentada después del plazo, seguida de la aprobación del conjunto antes de comparar modelos o prompts.
