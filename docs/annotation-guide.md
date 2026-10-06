# Guía de anotación — contrato 0.1.0

Esta guía define cómo construir las respuestas de referencia que EvalIA comparará con las salidas de modelos. Se comienza con textos de convocatorias en español y cuatro campos comprobables. La autoridad sobre forma, tipos y claves es [el esquema JSON](../schemas/evalia-case.schema.json); este documento define el significado de esos campos.

## Qué se anota

Un caso contiene el fragmento original completo en `text`, su procedencia, permiso de publicación, división del conjunto, estado de revisión, valores esperados y evidencia. Se conserva el texto tal como se recibió: cambiar espacios, tildes o saltos de línea después de anotar invalidaría las posiciones de las citas.

Los diez casos de arranque de la subtarea 0.2 están en `datasets/seed.jsonl` y son ejemplos ficticios identificados como tales. Su procedencia, inventario y fecha de revisión mínima están en [la documentación del conjunto](../datasets/README.md). Todavía no existe un conjunto aprobado mediante la revisión diferida.

| Campo esperado | Significado | Ausencia |
| --- | --- | --- |
| `closing_date` | Fecha límite explícita para postular, con día, mes y año. | `null` |
| `modality` | Modalidad explícita: `remota`, `hibrida` o `presencial`. | `null` |
| `skills` | Habilidades técnicas obligatorias que el fragmento menciona. | `[]` |
| `student_required` | `true` si exige ser estudiante; `false` si dice expresamente que no es necesario. | `null` |

Todas las claves se incluyen aunque no exista un valor. `null` representa información no determinable a partir del texto. Nunca se infiere una condición usando conocimiento de la institución, del país o del año actual.

## Decisiones por campo

### Fecha de cierre

- Convertir fechas explícitas a `YYYY-MM-DD` y comprobar que sean fechas de calendario válidas.
- Anotar el cierre de postulaciones; no confundirlo con publicación, entrevista o inicio de actividades.
- Si falta el año, usar `null`; no completarlo con la fecha del computador.
- Una mención inequívoca de «hasta el 15 de noviembre de 2026» corresponde a `2026-11-15`.
- Si hay dos cierres contradictorios sin aclaración explícita, dejar el campo en `null`, marcar el caso `review_required` y describir el conflicto. El caso completo queda fuera de la puntuación hasta resolverlo.
- Si un cierre sustituye explícitamente al anterior («se amplía el plazo hasta...»), usar el plazo actualizado e incluir la aclaración en la cita.

### Modalidad

- «Remota» o «a distancia» se normaliza a `remota`; «híbrida» a `hibrida`; «presencial» a `presencial`.
- «Flexible», una ubicación o una dirección por sí solas no determinan modalidad: usar `null`.
- Si el texto enumera modalidades alternativas sin fijar una, usar `null`; si las afirmaciones son contradictorias, marcar revisión.

### Habilidades

- Incluir únicamente habilidades técnicas obligatorias expresas. Las deseables o recomendadas se excluyen de este primer contrato.
- No completar habilidades a partir del título del cargo ni interpretar «conocimientos de informática» como Python, SQL u otra herramienta.
- Anotar cada habilidad una sola vez. Mantener términos distintos aunque suelan usarse juntos.
- El vocabulario de equivalencias será versionado antes de implementar la normalización: `Python 3`→`Python` y `sql`→`SQL` son equivalencias permitidas; `IA`→`Machine Learning` no lo es.
- Si una habilidad no tiene equivalencia documentada, conservar el término explícito, sin inventar una transformación tras observar resultados de modelos.
- Una lista vacía significa que el fragmento no contiene una habilidad técnica obligatoria explícita. No demuestra que el puesto carezca de requisitos en su convocatoria completa.

### Requisito de estudiante

- «Es obligatorio ser estudiante regular» corresponde a `true`.
- «No es necesario ser estudiante» corresponde a `false` y requiere una cita que contenga la negación.
- Si no se menciona esta condición, corresponde a `null`.
- Referencias generales a jóvenes, formación o carreras no prueban el requisito.
- Si el texto es contradictorio, marcar `review_required`; no sustituir el conflicto por una negativa.

## Evidencia y posiciones

Los campos escalares no nulos tienen una evidencia con `quote`, `start` y `end`. Si su valor es `null`, su evidencia también es `null`. Las habilidades tienen una entrada por término con `skill`, `quote`, `start` y `end`; si no hay habilidades, ambas listas están vacías.

Las posiciones son índices de puntos de código Unicode según las cadenas de Python, comenzando en cero. `start` se incluye y `end` se excluye: debe cumplirse `text[start:end] == quote`. El símbolo 📌 ocupa un punto de código; otros emojis pueden combinar varios, aunque visualmente parezcan un solo carácter. Los futuros consumidores de JavaScript deberán respetar esta convención. Una cita debe contener la información necesaria, incluida la negación o la obligatoriedad cuando corresponda.

Que una cita exista en el texto solo verifica su localización. La revisión humana debe comprobar que respalda el valor anotado.

## Procedencia, revisión y división

- `source_url` es opcional; puede ser una URL HTTP(S) o `null` para textos ficticios.
- `source_license` documenta la licencia o fundamento conocido. Si no está definido, se registra la incertidumbre y `redistribution_allowed=false`.
- `redistribution_allowed=true` solo se asigna tras comprobar que el texto puede publicarse. Este indicador no concede derechos por sí mismo.
- `split=seed` identifica casos de arranque; `dev` sirve para ajustar prompts; `test` identifica el conjunto final congelado.
- `review_status=draft` significa anotación inicial. `review_required` señala una ambigüedad pendiente y exige `review_notes`. `reviewed` significa que la revisión definida en el plan ya se realizó.
- Solo los casos `reviewed` participan en una evaluación final. Un borrador puede usarse para verificar el software, identificado como prueba de desarrollo.

## Qué puede comprobar cada capa

El esquema comprueba claves, tipos, enumeraciones, listas sin duplicados y la relación de nulidad entre valores y evidencias escalares. La validación de `format=date` requiere activar comprobación de formatos.

`evalia validate` comprueba identificadores y textos únicos entre líneas, texto no compuesto solo por espacios, límites y contenido literal de las citas, y correspondencia uno a uno entre habilidades y evidencias. Estas reglas entre valores no quedan garantizadas por JSON Schema. La composición específica del conjunto inicial se comprueba con `scripts/check_seed_cases.py`; el validador genérico no exige que todo conjunto tenga diez casos o la misma distribución de etiquetas.

La revisión humana comprobará interpretación, contradicciones, equivalencias, permiso de publicación y respaldo semántico. Esas comprobaciones no se presentarán como resueltas solo porque el archivo cumpla su esquema.

## Cambios del contrato

Una modificación de nombres, significado, nulidad o evidencia requiere versión nueva del esquema, actualización de esta guía y revisión de los casos afectados. Los modelos de datos que se incorporen al paquete Python deben derivarse de este contrato o verificarse contra él; no se mantendrá una segunda definición independiente.

## Reproducir la comprobación del esquema

Se verificó el contrato con `jsonschema` 4.26.0. El script usa ejemplos internos ficticios, activa comprobación de formatos y revisa respuestas válidas e inválidas. Desde la raíz, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install jsonschema==4.26.0
.\.venv\Scripts\python.exe scripts/check_case_contract.py
```

El resultado esperado es cuatro ejemplos válidos aceptados y catorce ejemplos inválidos rechazados. Esta comprobación no ejecuta modelos ni demuestra que exista un conjunto anotado y revisado. Las dependencias del paquete se organizarán en el paso 1.
