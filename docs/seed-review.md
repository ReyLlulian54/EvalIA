# Registro de revisión de los casos de arranque

## Estado y referencia

Subtarea 0.3 **en curso: preparación terminada; segunda lectura pendiente**. Este documento prepara el trabajo y conserva su referencia de entrada. No acredita revisión semántica ni aprobación de casos.

- Conjunto: [seed.jsonl](../datasets/seed.jsonl), versión `seed-0.1.0`.
- Commit de creación: `f0f26401955f25eeb5ce0f130567d301492e4e54`, integrado mediante la PR #2.
- Contrato autoritativo: [esquema 0.1.0](../schemas/evalia-case.schema.json).
- Criterios de interpretación: [guía de anotación](annotation-guide.md).
- Creación registrada: `2026-10-03T05:54:00Z`.
- Segunda lectura permitida desde: **`2026-10-04T05:54:00Z`**, equivalente al **4 de octubre a las 02:54 en America/Santiago**.
- Comprobación del intervalo el `2026-10-03T18:52:38Z`: habían pasado 12 horas, 58 minutos y 38 segundos. Aún no se cumplían las 24 horas del plan aprobado.
- Hash de entrada SHA-256, UTF-8 con saltos LF: `63523c2e9d52a055e06d3a561712d0c5fee3761cdf167313c8bc83487ac4040a`.

La comprobación mecánica realizada durante esta preparación confirma diez casos conformes, identificadores y textos únicos y 30 citas exactas. El conjunto mantiene nueve `draft` y un `review_required`; ningún caso está en `reviewed`.

## Procedimiento de la segunda lectura

1. Comprobar la hora real y el hash de entrada. Si cambió el contenido desde esta referencia, registrar el nuevo commit, hash y motivo antes de revisar. No dar por cumplido el intervalo para casos nuevos o textos que hayan cambiado durante la espera.
2. Registrar persona revisora, comienzo y fin reales. La IA puede ayudar a señalar inconsistencias; su comprobación no debe presentarse como revisión humana. Los criterios semánticos de la guía requieren lectura humana.
3. Leer el texto de cada caso y reconstruir primero los cuatro valores esperados, sin consultar la anotación existente. Después comparar con `expected` y examinar sus citas. Esto ayuda a detectar errores compartidos con la anotación inicial.
4. Aplicar la guía a cada campo, incluidos `null`, `false` y listas vacías. Verificar que las citas respalden el valor, no solo que existan en el texto. Comprobar obligatoriedad, negación y contexto de cada fecha.
5. Registrar por caso la decisión y el motivo. Si hay una discrepancia, anotar campo, valor anterior, valor corregido y explicación. Cambiar citas o texto exige recalcular posiciones; no completar datos ausentes usando conocimiento externo.
6. Marcar `reviewed` únicamente tras completar la lectura requerida y resolver sus discrepancias. Conservar `review_required` y notas cuando persista un conflicto; excluir ese caso completo de métricas finales. No inventar una fecha para resolver `seed-008`.
7. Si cambia el JSONL, actualizar versión del conjunto, hash de salida e inventario. Mantener el esquema 0.1.0 si su contrato no cambió. Ejecutar las comprobaciones existentes y revisar el diff antes del commit y la PR.

## Lista de trabajo por caso

Todas las decisiones siguientes están pendientes. La columna de foco identifica qué debe inspeccionarse; no contiene conclusiones de la segunda lectura.

| Caso | Foco de revisión | Decisión | Motivo o corrección |
| --- | --- | --- | --- |
| `seed-001` | Fecha completa y evidencia de obligatoriedad para ambas habilidades y estudiante. | Pendiente | Por registrar. |
| `seed-002` | Ausencia de cierre y diferencia entre habilidades obligatorias y Docker deseable. | Pendiente | Por registrar. |
| `seed-003` | Fecha de inicio frente a cierre, Python recomendado y cita de negación de estudiante. | Pendiente | Por registrar. |
| `seed-004` | Fecha sin año, referencia a jóvenes y modalidad a distancia. | Pendiente | Por registrar. |
| `seed-005` | Día bisiesto, horario flexible, dirección y equivalencia documentada de `sql`. | Pendiente | Por registrar. |
| `seed-006` | Duplicación de Python, obligatoriedad, saltos de línea y puntos de código de emojis compuestos. | Pendiente | Por registrar. |
| `seed-007` | Evidencia de sustitución del plazo y ausencia de requisito de estudiante. | Pendiente | Por registrar. |
| `seed-008` | Cierres incompatibles; comprobar notas y mantener exclusión si no hay resolución respaldada. | Pendiente | Por registrar. |
| `seed-009` | Modalidades alternativas, habilidades deseables y negación explícita de estudiante. | Pendiente | Por registrar. |
| `seed-010` | Tecnologías solo en el título, publicación e inicio, dirección y referencia a jóvenes. | Pendiente | Por registrar. |

## Resultado de la segunda lectura

- Persona revisora: **pendiente**.
- Apoyo de IA utilizado: **por registrar**.
- Comienzo y fin reales en UTC: **pendientes**.
- Casos examinados mediante segunda lectura: **0 de 10**.
- Correcciones: **por registrar tras la lectura**; no se afirma que sean cero.
- Casos aprobados: **0**.
- Conflictos resueltos: **por registrar**.
- Conflicto ya conocido: `seed-008`, todavía en `review_required`.
- Versión, commit y hash de salida: **pendientes**.

## Criterio de cierre de 0.3

La subtarea se completa cuando los diez casos tienen una decisión registrada tras la espera requerida, los casos aprobados tienen respaldo semántico revisado, los conflictos pendientes quedan identificados y excluidos, las correcciones están documentadas y las comprobaciones mecánicas pasan. El conjunto puede conservar un caso contradictorio para probar el tratamiento de exclusiones; no se debe presentarlo como un caso aprobado para puntuar modelos.

Esta preparación no cierra el paso 0 y no inicia el paso 1. El avance debe registrarse en [la bitácora](progress.md) después de realizar la segunda lectura.
