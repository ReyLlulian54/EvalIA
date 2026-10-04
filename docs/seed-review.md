# Registro de revisión de los casos de arranque

## Estado y referencia

Subtarea 0.3 **en curso: segunda lectura asistida por IA terminada; validación humana pendiente**. Este documento conserva la referencia de entrada y las decisiones de la lectura realizada después del intervalo. No presenta la comprobación de IA como revisión humana ni cambia todavía los estados del conjunto.

- Conjunto: [seed.jsonl](../datasets/seed.jsonl), versión `seed-0.1.0`.
- Commit de creación: `f0f26401955f25eeb5ce0f130567d301492e4e54`, integrado mediante la PR #2.
- Contrato autoritativo: [esquema 0.1.0](../schemas/evalia-case.schema.json).
- Criterios de interpretación: [guía de anotación](annotation-guide.md).
- Creación registrada: `2026-10-03T05:54:00Z`.
- Segunda lectura permitida desde: **`2026-10-04T05:54:00Z`**, equivalente al **4 de octubre a las 02:54 en America/Santiago**.
- Comprobación del intervalo el `2026-10-03T18:52:38Z`: habían pasado 12 horas, 58 minutos y 38 segundos. Aún no se cumplían las 24 horas del plan aprobado.
- Comienzo de la segunda lectura asistida: `2026-10-04T20:12:15Z`, equivalente al 4 de octubre a las 17:12 en America/Santiago. Habían transcurrido 38 horas, 18 minutos y 15 segundos desde la creación.
- Hash de entrada SHA-256, UTF-8 con saltos LF: `63523c2e9d52a055e06d3a561712d0c5fee3761cdf167313c8bc83487ac4040a`.

La comprobación mecánica confirma diez casos conformes, identificadores y textos únicos y 30 citas exactas. La segunda lectura asistida reconstruyó los cuatro campos de cada caso, los comparó con las anotaciones y revisó el respaldo semántico de las citas. No encontró discrepancias en los nueve casos determinables y confirmó que el conflicto de `seed-008` no puede resolverse con el texto disponible.

## Procedimiento de la segunda lectura

1. Comprobar la hora real y el hash de entrada. Si cambió el contenido desde esta referencia, registrar el nuevo commit, hash y motivo antes de revisar. No dar por cumplido el intervalo para casos nuevos o textos que hayan cambiado durante la espera.
2. Registrar persona revisora, comienzo y fin reales. La IA puede ayudar a señalar inconsistencias; su comprobación no debe presentarse como revisión humana. Los criterios semánticos de la guía requieren lectura humana.
3. Leer el texto de cada caso y reconstruir primero los cuatro valores esperados, sin consultar la anotación existente. Después comparar con `expected` y examinar sus citas. Esto ayuda a detectar errores compartidos con la anotación inicial.
4. Aplicar la guía a cada campo, incluidos `null`, `false` y listas vacías. Verificar que las citas respalden el valor, no solo que existan en el texto. Comprobar obligatoriedad, negación y contexto de cada fecha.
5. Registrar por caso la decisión y el motivo. Si hay una discrepancia, anotar campo, valor anterior, valor corregido y explicación. Cambiar citas o texto exige recalcular posiciones; no completar datos ausentes usando conocimiento externo.
6. Marcar `reviewed` únicamente tras completar la lectura requerida y resolver sus discrepancias. Conservar `review_required` y notas cuando persista un conflicto; excluir ese caso completo de métricas finales. No inventar una fecha para resolver `seed-008`.
7. Si cambia el JSONL, actualizar versión del conjunto, hash de salida e inventario. Mantener el esquema 0.1.0 si su contrato no cambió. Ejecutar las comprobaciones existentes y revisar el diff antes del commit y la PR.

## Lista de trabajo por caso

Las decisiones siguientes registran la segunda lectura asistida. «Consistente» significa que la anotación coincide con el texto y la guía; no equivale a validación humana ni cambia `review_status` por sí sola.

| Caso | Foco de revisión | Decisión | Motivo o corrección |
| --- | --- | --- | --- |
| `seed-001` | Fecha completa y evidencia de obligatoriedad para ambas habilidades y estudiante. | Consistente | Cierre `2026-11-15`, modalidad remota, Python y SQL obligatorios y estudiante `true` están explícitos. Las citas contienen la obligatoriedad. |
| `seed-002` | Ausencia de cierre y diferencia entre habilidades obligatorias y Docker deseable. | Consistente | El texto declara que no informa cierre; Python y Git son requisitos, Docker solo deseable; modalidad híbrida y estudiante `true` están explícitos. |
| `seed-003` | Fecha de inicio frente a cierre, Python recomendado y cita de negación de estudiante. | Consistente | La única fecha corresponde al inicio; SQL es obligatorio, Python recomendado; la negación respalda estudiante `false`. |
| `seed-004` | Fecha sin año, referencia a jóvenes y modalidad a distancia. | Consistente | El cierre sin año queda `null`; «a distancia» respalda remota; Python recomendado se excluye y «jóvenes» no prueba requisito de estudiante. |
| `seed-005` | Día bisiesto, horario flexible, dirección y equivalencia documentada de `sql`. | Consistente | `2028-02-29` es válida; horario y dirección no determinan modalidad; Docker y SQL son obligatorios y la negación respalda estudiante `false`. |
| `seed-006` | Duplicación de Python, obligatoriedad, saltos de línea y puntos de código de emojis compuestos. | Consistente | Fecha, modalidad y estudiante son explícitos; Python se anota una vez pese a repetirse y Git comparte una cita obligatoria válida. Las posiciones siguen la convención de Python. |
| `seed-007` | Evidencia de sustitución del plazo y ausencia de requisito de estudiante. | Consistente | La ampliación sustituye expresamente el cierre anterior por `2026-12-20`; modalidad remota y Python obligatorio están explícitos; estudiante queda `null`. |
| `seed-008` | Cierres incompatibles; comprobar notas y mantener exclusión si no hay resolución respaldada. | Conflicto confirmado | Las fechas `2026-11-15` y `2026-11-18` se contradicen sin sustitución. Mantener `closing_date=null`, `review_required` y exclusión completa de métricas. Los demás campos están respaldados, pero no habilitan el caso para puntuación. |
| `seed-009` | Modalidades alternativas, habilidades deseables y negación explícita de estudiante. | Consistente | La fecha está completa; dos modalidades alternativas no fijan una; Python y Git son deseables; la negación respalda estudiante `false`. |
| `seed-010` | Tecnologías solo en el título, publicación e inicio, dirección y referencia a jóvenes. | Consistente | Título, publicación, inicio, dirección y referencia a jóvenes no prueban cierre, modalidad, habilidades obligatorias ni requisito de estudiante. Corresponden `null`, `null`, `[]` y `null`. |

## Resultado de la segunda lectura

- Persona revisora humana: **pendiente**.
- Apoyo de IA utilizado: **Codex realizó una segunda lectura semántica y mecánica solicitada por la persona responsable del proyecto**.
- Comienzo de la lectura asistida en UTC: `2026-10-04T20:12:15Z`.
- Fin de la lectura asistida en UTC: `2026-10-04T20:13:03Z`.
- Casos examinados mediante segunda lectura asistida: **10 de 10**.
- Correcciones propuestas por la lectura asistida: **0**.
- Casos aprobados: **0**.
- Casos consistentes listos para validación humana: **9**.
- Conflictos resueltos: **0**.
- Conflicto confirmado: `seed-008`, todavía en `review_required` y excluido de métricas.
- Versión y hash: se conserva `seed-0.1.0` y el hash de entrada, porque no cambió `datasets/seed.jsonl`.

## Validación humana pendiente

La persona responsable debe leer los diez textos y las decisiones de la tabla. Si coincide con los nueve casos consistentes, registrará su nombre y fecha, cambiará esos nueve estados de `draft` a `reviewed` y mantendrá `seed-008` en `review_required`. Si encuentra una discrepancia, debe registrar el campo, el valor anterior y la corrección antes de modificar el JSONL. Después se calculará el hash de salida y se repetirán las comprobaciones.

## Criterio de cierre de 0.3

La subtarea se completa cuando los diez casos tienen una decisión registrada tras la espera requerida, los casos aprobados tienen respaldo semántico revisado, los conflictos pendientes quedan identificados y excluidos, las correcciones están documentadas y las comprobaciones mecánicas pasan. El conjunto puede conservar un caso contradictorio para probar el tratamiento de exclusiones; no se debe presentarlo como un caso aprobado para puntuar modelos.

La lectura asistida no cierra el paso 0 ni inicia el paso 1. La subtarea 0.3 se cerrará después de la validación humana y de actualizar los estados del conjunto con evidencia registrada.
