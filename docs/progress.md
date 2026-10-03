# Bitácora de implementación

## 3 de octubre de 2026 — inicio del proyecto

El plan de implementación está aprobado. El repositorio se organiza en entregas pequeñas con Conventional Commits y GitHub Flow, apoyados por las guías de ECC.

### Paso 0 — contrato y casos de arranque

| Subtarea | Estado | Entregable |
| --- | --- | --- |
| 0.1. Definir contrato y guía de anotación | Completada | Esquema JSON autoritativo 0.1.0 y decisiones de anotación. |
| 0.2. Crear diez casos de arranque | Completada | Diez textos ficticios anotados, inventario y comprobación de 30 citas. |
| 0.3. Revisar los casos después de al menos 24 horas | Pendiente | Registro de correcciones y casos aprobados. |

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
