# Rúbrica de evaluación — paso 3

La evaluación recibe un caso de referencia y una predicción con los cuatro campos de extracción. La forma de ambos se comprueba contra el [esquema autoritativo 0.1.0](../schemas/evalia-case.schema.json): la predicción usa `$defs/extraction` del mismo archivo, sin una segunda definición de campos. Los valores deben llegar normalizados según [las reglas versionadas](normalization.md). El evaluador no modifica el texto, las citas ni la predicción.

## Subtareas

1. **3.1 — puntaje por caso:** validar las entradas, excluir casos no revisados y devolver conteos por campo. Esta entrega implementa `evalia.graders.core.grade_case`.
2. **3.2 — métricas del conjunto:** agregar numeradores, denominadores y casos fallidos; medir abstención y evidencia literal; separar fallos de formato de fallos de contenido.
3. **3.3 — línea base y reporte:** añadir reglas sin IA para el primer conjunto y un reporte verificable con los mismos denominadores.

## Reglas de 3.1

Solo `review_status=reviewed` se puntúa. `draft` y `review_required` producen `ExcludedCase` con el motivo y no aportan denominadores. El estado del archivo es un registro de revisión; el código no puede sustituir la comprobación humana de su veracidad.

| Campo | Conteo por caso revisado |
| --- | --- |
| `closing_date` | 1/1 si coincide exactamente; 0/1 si no. `null` coincide solo con `null`. |
| `modality` | 1/1 si coincide exactamente; 0/1 si no. |
| `student_required` | 1/1 si coincide exactamente; 0/1 si no. `false` y `null` son distintos. |
| `skills_exact` | 1/1 si los conjuntos de habilidades coinciden, sin depender del orden; 0/1 si no. |
| Habilidades por elemento | `TP` = presentes en ambos conjuntos; `FP` = predichas y ausentes de la referencia; `FN` = omitidas. Precisión = `TP/(TP+FP)`, cobertura = `TP/(TP+FN)` y F1 = `2TP/(2TP+FP+FN)`. |

Cada razón conserva numerador y denominador. Si el denominador es cero, `value=None` indica **no aplicable**, nunca 100 %. Con ambos conjuntos de habilidades vacíos, `skills_exact=1/1`, mientras que precisión, cobertura y F1 son `0/0` con valor no aplicable. Si la referencia contiene habilidades y la predicción está vacía, la precisión es no aplicable y la cobertura es cero.

Ejemplo puramente sintético: referencia `["Python", "SQL"]` frente a predicción `["Python", "Docker"]` produce `TP=1`, `FP=1`, `FN=1`, precisión `1/2`, cobertura `1/2`, F1 `2/4` y coincidencia exacta `0/1`. No es una medición de un modelo.

Una predicción con tipos, claves, modalidades o fechas fuera del contrato genera un error de validación; una habilidad no canónica genera un error explícito. Un valor bien formado pero equivocado aparece como fallo de contenido en `CaseGrade.failed_fields`. El evaluador comprueba la estructura y coherencia mecánica del caso de referencia antes de puntuar, pero no decide si una cita respalda semánticamente su etiqueta. La agregación y la puntuación de evidencia pertenecen a 3.2.

```python
from evalia.graders.core import grade_case

# case: caso revisado y validado; prediction: extracción canónica de cuatro campos.
outcome = grade_case(case, prediction)
```
