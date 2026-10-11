# Benchmark v1 — referencia revisada y partición de prueba congelada

El archivo [benchmark-v1.jsonl](../datasets/benchmark-v1.jsonl) contiene **36 convocatorias ficticias originales** redactadas para EvalIA, con anotaciones y evidencia literal. No corresponden a becas, prácticas ni empleos reales. La persona responsable confirmó como conformes los 36 casos de la instantánea borrador identificada por su hash; después se cambió únicamente `review_status` a `reviewed`. La [revisión asistida](benchmark-v1-review.md) y la confirmación humana están registradas por separado. El conjunto es una referencia revisada para experimentos reproducibles, pero todavía no existen resultados comparativos de modelos ni evidencia de representatividad sobre convocatorias reales.

La estructura de cada línea procede únicamente del [esquema de casos 0.1.0](../schemas/evalia-case.schema.json); la [guía de anotación](annotation-guide.md) define el significado de los campos. El [manifiesto](../datasets/benchmark-v1-manifest.json) fija el hash del conjunto final, los identificadores y el hash del contenido de `test`; no duplica las respuestas esperadas.

## Diseño fijado antes de evaluar modelos

- Tamaño: 36 casos, con 27 `dev` y 9 `test` (25 %).
- Partición `test`: `bench-001`, `bench-007`, `bench-011`, `bench-015`, `bench-017`, `bench-022`, `bench-027`, `bench-031` y `bench-033`. Estos IDs se eligieron antes de ejecutar modelos sobre este conjunto y no se usarán para ajustar prompts. Incluyen 3 requisitos de estudiante `true`, 3 `false` y 3 `null`, además de casos sin habilidades obligatorias.
- Procedencia: textos ficticios escritos para el proyecto, `source_url=null` y `source_license=LicenseRef-EvalIA-Original`. No se copiaron anuncios externos. `redistribution_allowed=true` registra su publicación prevista en el repositorio; el identificador no es una licencia estándar.
- Estado: 36 `reviewed` tras la confirmación humana registrada. La validación mecánica por sí sola no cambia ese estado.
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

El borrador con la partición fijada se escribió el **2026-10-09T02:26:36Z** (8 de octubre a las 23:26 en America/Santiago), con hash LF `aac3b05a1b67ada1a9db66d703c00ee6df60a91cd9bb8865eef8954f863aad34`. Tras dos correcciones editoriales el **2026-10-10T22:02:58Z**, la instantánea presentada para revisión humana fue `benchmark-v1-draft-0.1.1`, con SHA-256 del JSONL UTF-8 normalizado a LF `b4ee52f0c16ea937a87c112540a37d2ca5424c6792c9a2e1cdd88856c35e8b0d`.

La versión final `benchmark-v1-1.0.0` se registró el **2026-10-11T22:47:52Z** con hash LF completo `598740b54573749e6c7eb9007117f39d9fc971c7a1ee93550a44243d22c0926c` y hash LF de `test` `86dca1777e7b3dbb4dd523d3204f797f2ed5b2f6b42d4cb7d92334ec87b40e34`. Para este último se toman las nueve líneas JSONL `test` en su orden original, se normalizan los saltos a LF y se calcula SHA-256 sobre su concatenación con un LF final. El comprobador verifica tanto el hash global como el de `test`; la huella de `test` permite detectar su modificación incluso si se actualiza el hash global. La normalización LF estabiliza la comprobación entre Windows y otros sistemas; el motor de ejecución registra por separado el hash de los bytes exactos que recibe.

Desde la raíz del repositorio, con el entorno de desarrollo instalado:

```powershell
.\.venv\Scripts\evalia validate datasets\benchmark-v1.jsonl
.\.venv\Scripts\python scripts\check_benchmark_v1.py
```

El primer comando consume el contrato autoritativo y comprueba sintaxis, forma, unicidad, habilidades canónicas y citas literales. El segundo comprueba los dos hashes, procedencia, estados, tamaño, cobertura y partición. Ninguno demuestra que una cita respalde semánticamente su etiqueta. Si se corrige un texto o una anotación, registrar motivo y nueva versión y volver a revisar los casos afectados; un cambio en `test` exige además una nueva confirmación humana antes de actualizar su huella. No cambiar silenciosamente los IDs de `test`.

## Revisión y mantenimiento

1. **Primera lectura de los 36 casos:** reconstruir fecha, modalidad, habilidades y requisito de estudiante desde cada `text`, sin mirar primero `expected`; comparar después cada valor y su cita. Comprobar en especial que `false` contenga negación explícita, que las habilidades sean obligatorias y que la fecha citada sea el cierre vigente. Registrar correcciones y responsable de la revisión. La creación asistida y la validación mecánica no sustituyen esta lectura humana.
2. **Segunda lectura tras al menos 24 horas:** la muestra fijada es `bench-001`, `bench-006`, `bench-011`, `bench-014`, `bench-017`, `bench-022`, `bench-027`, `bench-029` y `bench-033`. Nueve de 36 equivalen al 25 %, por encima del mínimo del plan de 20 %. La revisión asistida completó los nueve casos; los dos textos corregidos se releyeron después de su nuevo plazo y el resultado se registró en el [acta](benchmark-v1-review.md).
3. **Cierre realizado:** la persona responsable confirmó como conformes los 36 casos de la instantánea borrador con hash `b4ee52f0c16ea937a87c112540a37d2ca5424c6792c9a2e1cdd88856c35e8b0d`. Se pasó a `reviewed` sin modificar textos, etiquetas, citas, partición ni procedencia, se creó `benchmark-v1-1.0.0` y se fijó la huella de `test`. El [acta](benchmark-v1-review.md) distingue la confirmación comunicada por la persona responsable de la revisión asistida previa.

La segunda lectura asistida está **9/9** y la confirmación humana de la instantánea está registrada. La [hoja de revisión humana](benchmark-v1-human-review.md) conserva la correspondencia de los 36 IDs. Cualquier corrección posterior del conjunto revisado requiere motivo, nueva versión, hashes renovados y revisión humana de los casos afectados antes de usar una nueva referencia.
