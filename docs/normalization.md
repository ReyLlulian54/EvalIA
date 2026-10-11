# Normalización de fechas y habilidades

Estas reglas preparan candidatos para compararlos con el contrato de casos 0.1.0. `evalia validate` exige que los valores de referencia ya sean canónicos: informa los alias de habilidades, pero **no reescribe** el JSONL ni las citas. La normalización de un candidato no demuestra que la fecha sea de cierre o que una habilidad sea obligatoria; eso depende del texto y de la revisión de la anotación.

## Versiones y fuentes

- Fechas: `DATE_RULES_VERSION = "1.0.0"` en `src/evalia/normalization.py`. Cambiar los formatos aceptados o el tratamiento de ausencias requiere actualizar esta versión y sus pruebas.
- Habilidades: versión `1.0.0` declarada en [`skills-v1.json`](../src/evalia/vocabularies/skills-v1.json). Ese archivo es la única lista autoritativa de alias; cualquier equivalencia nueva se añade allí antes de comparar resultados y obliga a revisar los casos afectados.
- La estructura y los valores permitidos del caso siguen definidos solo en [`evalia-case.schema.json`](../schemas/evalia-case.schema.json). Estas reglas no alteran su versión.

## Fechas

`normalize_date` recibe una fecha candidata, no un párrafo completo. Acepta `YYYY-MM-DD`, `D/M/YYYY` en orden día/mes/año y `D de mes de YYYY` con el mes español. Admite ceros iniciales opcionales en día y mes, diferencias de mayúsculas y espacios exteriores o repetidos. Devuelve ISO `YYYY-MM-DD` y usa el calendario real, incluidos años bisiestos.

| Entrada | Salida |
| --- | --- |
| `2026-11-15` | `2026-11-15` |
| `5 de diciembre de 2026` | `2026-12-05` |
| `29/02/2028` | `2028-02-29` |
| `15 de noviembre` o `15/11` | `None` (`null` al serializar) |
| `None` o cadena vacía | `None` |
| `2026-02-29`, `31/04/2026`, `01-02-2026` | Error `ValueError` |

Una fecha reconocible sin año queda desconocida: no se completa con el año actual. Los formatos no reconocidos y las fechas imposibles producen un error explícito. Valores que no sean texto o `None`, incluido `False`, producen `TypeError`. Una fecha de inicio, entrevista o publicación no se convierte automáticamente en cierre.

## Habilidades

`normalize_skill` quita espacios exteriores, comprime espacios interiores y busca el nombre con comparación sin distinguir mayúsculas. El vocabulario 1.0.0 permite `Python`, `Python 3` y `Python3` → `Python`; `sql` → `SQL`; y las variantes de mayúsculas de `Git` y `Docker`. Un término sin alias conserva su escritura limpiada: `IA` sigue siendo `IA`, sin inferir `Machine Learning`. Un término vacío produce `ValueError`.

`normalize_skills` aplica esas reglas a una colección y elimina equivalentes repetidos conservando el orden de primera aparición. Por ejemplo, `["sql", "Python 3", "SQL", "Git"]` produce `["SQL", "Python", "Git"]`. No decide si una habilidad es obligatoria o deseable, y no cambia los fragmentos literales guardados en `evidence`.

```python
from evalia.normalization import normalize_date, normalize_skills

normalize_date("15 de noviembre de 2026")  # "2026-11-15"
normalize_skills(["Python 3", "sql"])       # ["Python", "SQL"]
```

La distinción `student_required=false` frente a `null` pertenece al contrato y no se transforma con estas funciones. Para comprobar las reglas junto con los diez casos iniciales: `python -m pytest tests/test_normalization.py tests/test_validate.py` y `evalia validate datasets/seed.jsonl`.
