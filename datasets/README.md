# Casos de arranque — seed 0.1.1

El borrador del conjunto ampliado está en [benchmark-v1.jsonl](benchmark-v1.jsonl); su [diseño y revisión pendiente](../docs/benchmark-v1.md) se documentan por separado. Sus 36 casos siguen en `draft` y no deben confundirse con los nueve casos `seed` ya revisados.

[seed.jsonl](seed.jsonl) contiene diez convocatorias ficticias en español, redactadas con asistencia de IA específicamente para EvalIA. No corresponden a oportunidades reales y no se copiaron de sitios externos. Sirven para comprobar el contrato y comenzar el desarrollo; no permiten concluir qué modelo es mejor para convocatorias reales.

Cada línea sigue [el contrato 0.1.0](../schemas/evalia-case.schema.json) y [la guía de anotación](../docs/annotation-guide.md). Se incluyen valores esperados y citas literales con índices de puntos de código Unicode de Python. No se cambió el contrato para acomodar los ejemplos.

## Procedencia y publicación

Todos los registros tienen `source_url=null`, `split=seed` y `source_license=LicenseRef-EvalIA-Original`. Este identificador registra que el texto fue creado para el proyecto; no es una licencia estándar ni concede por sí mismo derechos de reutilización. `redistribution_allowed=true` registra la publicación autorizada de estos textos originales en el repositorio. La licencia de distribución del proyecto se definirá en el paso 1.

## Inventario y decisiones iniciales

| ID | Situación | Decisión de anotación |
| --- | --- | --- |
| `seed-001` | Beca con todos los campos explícitos | Fecha completa, remota, Python y SQL obligatorios, estudiante `true`. |
| `seed-002` | Práctica sin cierre y con Docker deseable | Fecha `null`; incluir Python y Git, excluir Docker. |
| `seed-003` | Vacante con fecha de inicio y negación de requisito | No confundir inicio con cierre; estudiante `false`; excluir Python recomendado. |
| `seed-004` | Cierre sin año y orientación a jóvenes | Fecha y estudiante `null`; «a distancia» se normaliza a remota; Python recomendado se excluye. |
| `seed-005` | Cierre en día bisiesto y horario flexible | Fecha válida `2028-02-29`; horario y dirección no prueban modalidad; `sql` se normaliza a SQL. |
| `seed-006` | Texto multilínea, emojis y habilidad repetida | Índices según Python; una sola entrada para Python; conservar obligatoriedad en las citas. |
| `seed-007` | Ampliación explícita del plazo | Elegir el cierre nuevo y citar la ampliación; estudiante `null` por ausencia. |
| `seed-008` | Dos cierres incompatibles | Fecha `null`, estado `review_required` y notas; excluir todo el caso de métricas finales. |
| `seed-009` | Modalidades alternativas y habilidades deseables | Modalidad `null`, habilidades `[]`, estudiante `false` por negación explícita. |
| `seed-010` | Título con tecnologías, publicación e inicio | Ninguna tecnología obligatoria demostrada; cierre, modalidad y estudiante `null`. |

La anotación inicial contiene cinco fechas no determinables: cuatro por ausencia de cierre completo y una por contradicción. El requisito de estudiante tiene cuatro valores `true`, tres `false` y tres `null`. Tres casos tienen habilidades vacías. Hay 30 citas de evidencia, contando cada habilidad por separado aunque comparta cita con otra.

## Estado de revisión

Registro de creación del conjunto: **2026-10-03T05:54:00Z**. La persona responsable confirmó la revisión el **2026-10-04T21:40:29Z**. Nueve casos están en `reviewed`; `seed-008` permanece en `review_required` y excluido de métricas.

La segunda lectura de la subtarea 0.3 estaba permitida **a partir de 2026-10-04T05:54:00Z**, después de al menos 24 horas. Revisó significado y respaldo de cada respuesta, no encontró correcciones y conservó el conflicto sin puntuar. La persona responsable confirmó las decisiones registradas; todavía no hay métricas de modelos.

El [registro de revisión](../docs/seed-review.md) contiene la lectura asistida, la confirmación humana y el cierre de la subtarea. El cambio de estados produjo la versión `seed-0.1.1`, con hash SHA-256 `5fd3ffb891ccdca1b7cdf4642af2dc7b547438eda8d3e4766e0af5a26e3ea78e`. El contrato de cada registro sigue siendo 0.1.0 porque no cambió su estructura.

Una modificación posterior de textos, valores o citas debe registrarse en la bitácora y actualizar la versión del conjunto. Si cambia el contrato, también se debe revisar cada caso afectado.

## Repetir las comprobaciones

Con `jsonschema==4.26.0` en el entorno indicado en la guía, ejecutar desde la raíz:

```powershell
python scripts/check_case_contract.py
python scripts/check_seed_cases.py
```

La primera comprobación conserva los ejemplos positivos y negativos del contrato. La segunda revisa los diez casos, identificadores y textos únicos, tipos y fechas, correspondencia de habilidades y evidencia, límites y coincidencia exacta de 30 citas, además de la cobertura mínima de arranque. Muestra un hash SHA-256 del JSONL leído como UTF-8 con saltos normalizados a LF para identificar el contenido verificado en Windows y otros sistemas.

El script es una comprobación acotada a este conjunto. La CLI general del paso 2 sigue pendiente. La validación mecánica por sí sola no demuestra respaldo semántico ni representatividad de la muestra; el respaldo semántico de estos diez casos se revisó mediante el procedimiento documentado.
