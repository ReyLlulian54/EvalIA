# Rúbrica de evaluación — paso 3

La evaluación recibe un caso de referencia y una predicción con los cuatro campos de extracción. La forma de ambos se comprueba contra el [esquema autoritativo 0.1.0](../schemas/evalia-case.schema.json): la extracción usa `$defs/extraction` y las citas usan `$defs/evidence` del mismo archivo, sin una segunda definición de campos. Los valores deben llegar normalizados según [las reglas versionadas](normalization.md). El evaluador no modifica el texto, las citas ni la predicción.

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

Una predicción con tipos, claves, modalidades o fechas fuera del contrato genera un error de validación; una habilidad no canónica genera un error explícito. Un valor bien formado pero equivocado aparece como fallo de contenido en `CaseGrade.failed_fields`. El evaluador comprueba la estructura y coherencia mecánica del caso de referencia antes de puntuar, pero no decide si una cita respalda semánticamente su etiqueta.

```python
from evalia.graders.core import grade_case

# case: caso revisado y validado; prediction: extracción canónica de cuatro campos.
outcome = grade_case(case, prediction)
```

## Reglas de 3.2

`evaluate_dataset(cases, predictions)` recibe casos de referencia y registros con `case_id`, `extraction` y `evidence`. La extracción y evidencia se validan con las definiciones del esquema autoritativo. El identificador enlaza registros con casos; los metadatos adicionales del registro no participan del puntaje. Los IDs de referencia deben ser únicos. Una referencia inválida detiene la evaluación, pues no es un error atribuible a la predicción.

Solo los casos `reviewed` son elegibles. Una predicción ausente, duplicada o con extracción inválida figura en `format_errors` y no aporta denominadores de contenido. `coverage` muestra cuántos casos elegibles recibieron una extracción válida. Una predicción para un ID desconocido también figura como error de formato. Las predicciones de casos excluidos no se puntúan. El informe contiene `scored_case_ids` y exclusiones explícitas.

| Métrica | Numerador / denominador | Casos fallidos |
| --- | --- | --- |
| `coverage` | Extracciones válidas / casos revisados elegibles | Elegibles sin extracción válida. |
| Cada campo escalar y `skills_exact` | Coincidencias exactas / extracciones válidas | Valores distintos del esperado. |
| `skills_precision`, `skills_recall`, `skills_f1` | Conteos `TP/FP/FN` **sumados** en todo el conjunto; fórmulas de 3.1 | Casos con FP, FN o ambos, respectivamente. |
| `abstention.<campo>` | `null` predicho correctamente / referencias `null` para ese campo, entre extracciones válidas | Casos con referencia `null` y predicción no nula. Se mide por cada campo escalar; `false` no es abstención. |
| `evidence_literal` | Citas cuyo rango y texto coinciden literalmente / valores no nulos y habilidades **predichos** en extracciones válidas | Casos con una o más citas inválidas o faltantes. |

Para evidencia, una forma inválida, una cita ausente para un valor predicho o una correspondencia de habilidades distinta de 1:1 se registra en `format_errors` y aporta cero aciertos de cita para ese caso; su extracción válida **sí** conserva el puntaje de contenido. Una cita bien formada con texto o rango incorrecto falla en `evidence_literal` sin convertirse en error de formato. Los `null` y listas vacías no exigen cita. El rango usa índices Unicode de Python. Una coincidencia literal solo prueba trazabilidad de caracteres: no verifica que el fragmento respalde semánticamente el valor ni que la extracción sea correcta. Esa revisión seguirá siendo humana en la comparación final.

Cada métrica conserva `Ratio(numerator, denominator)` y `failed_case_ids`; con denominador cero, `value=None` significa **no aplicable**. No se calcula una puntuación compuesta ni se atribuyen los ejemplos sintéticos a modelos.

```python
from evalia.graders.dataset import evaluate_dataset

report = evaluate_dataset(
    [case],
    [{"case_id": case["id"], "extraction": prediction, "evidence": predicted_evidence}],
)
print(report.metric("coverage").ratio)
```

## Reglas de 3.3

La [línea base por reglas](baseline.md) usa exclusivamente el texto y el identificador de cada caso revisado; su salida entra a `evaluate_dataset` con el mismo contrato de predicción y los mismos denominadores. El [reporte JSON versionado](../examples/results/seed-baseline-v1.json) registra predicciones, citas, métricas, casos fallidos, exclusiones y hashes de insumos. La comprobación `python scripts/generate_seed_baseline.py --check` falla si el reporte no coincide con el código o los datos actuales.

El conjunto inicial es ficticio, pequeño y visible durante el desarrollo. Sus resultados sirven para comprobar el flujo de evaluación, no para estimar rendimiento de modelos ni generalización.
