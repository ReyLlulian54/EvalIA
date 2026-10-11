# Línea base por reglas — versión 0.1.0

La [línea base](../src/evalia/graders/baseline.py) recibe únicamente **case_id** y **text**. No lee respuestas esperadas, evidencia, estado de revisión ni metadatos de procedencia. Devuelve una extracción con las cuatro claves del contrato y citas literales con índices Unicode de Python. La [rúbrica](scoring.md) puntúa esas salidas sin distinguir su origen.

## Reglas y límites

- **Fecha de cierre:** busca fechas completas ISO, numéricas o textuales en cláusulas con una señal de postulación o cierre y las normaliza con las reglas 1.0.0. Si hay fechas distintas, se abstiene salvo que una cláusula indique explícitamente una ampliación. No usa fechas de publicación o inicio ni infiere años ausentes.
- **Modalidad:** reconoce menciones explícitas de remota, híbrida, presencial o «a distancia». Ante categorías distintas en el mismo texto devuelve null. Una dirección u horario flexible no bastan.
- **Habilidades:** busca alias del [vocabulario versionado](../src/evalia/vocabularies/skills-v1.json) solo en cláusulas con señales de obligatoriedad. Conserva una cita por habilidad canónica y descarta repeticiones. No convierte términos deseables o recomendados en requisitos.
- **Estudiante:** reconoce exigencia explícita como true y negación explícita como false; si no hay una declaración clara o hay conflicto, devuelve null.

Las cláusulas se separan por puntuación fuerte, punto y coma o salto de línea. Estas reglas tienen cobertura limitada: por ejemplo, «se solicita experiencia en Python» no coincide con las señales de obligatoriedad actuales. Las citas muestran dónde aparece el texto, pero no prueban por sí solas que la interpretación sea correcta. No se añadió aprendizaje automático ni llamadas a proveedores.

## Reporte del conjunto inicial

El [reporte JSON](../examples/results/seed-baseline-v1.json) incluye las nueve predicciones puntuadas, cada evidencia, los numeradores, denominadores, casos fallidos, errores de formato y la exclusión de seed-008. Registra hashes SHA-256 del conjunto, código de reglas, esquema y vocabulario. El archivo omite fecha de generación para que pueda compararse byte a byte entre ejecuciones. El generador rechaza casos sin permiso de redistribución.

| Medida | Resultado en seed-0.1.1 |
| --- | ---: |
| Cobertura y exactitud de cada campo | 9/9 |
| Habilidades: precisión y cobertura micro | 10/10 y 10/10 |
| Habilidades: F1 micro | 20/20 |
| Abstención correcta: fecha, modalidad, estudiante | 4/4, 3/3, 3/3 |
| Citas literales | 27/27 |
| Errores de formato | 0 |
| Excluidos por revisión pendiente | 1 (seed-008) |

Estos diez casos son ficticios, de arranque y estuvieron visibles durante el desarrollo de las reglas. Las cifras verifican el recorrido técnico sobre este conjunto; **no estiman calidad en convocatorias reales ni son resultados de un modelo**. No hay un conjunto final congelado para medir generalización. La ampliación y división de datos pertenecen al paso 5.

## Reproducir y comprobar

Desde la raíz del repositorio, con el entorno de desarrollo instalado:

~~~powershell
.\.venv\Scripts\evalia validate datasets\seed.jsonl
.\.venv\Scripts\python scripts\generate_seed_baseline.py --check
.\.venv\Scripts\python -m pytest tests\graders
~~~

La opción --check reconstruye las predicciones y métricas y compara el JSON versionado con el resultado actual; sale con código distinto de cero si falta o está obsoleto. Cuando cambien reglas, contrato o datos, revisar el motivo, volver a validar y regenerar explícitamente con --write; el diff del reporte debe revisarse antes de integrar. La comparación de hashes normaliza saltos de línea CRLF a LF al leer archivos UTF-8.
