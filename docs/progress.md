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
