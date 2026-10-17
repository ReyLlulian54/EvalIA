# Exportación segura — 6.d

`evalia export-public` construye un **candidato estructurado** a partir del conjunto, las dos corridas y la comparación reauditoradas. No ejecuta modelos ni publica el archivo. Su contrato único de salida es [`evalia-public-report.schema.json`](../schemas/evalia-public-report.schema.json) 0.1.0. Solo incluye IDs, split, etiquetas y predicciones de cuatro campos, categorías, conteos, tiempos y hashes de procedencia. `text`, citas, `raw_text`, prompt compuesto, registros de permisos, rutas locales y secretos no se copian.

La selección requiere un registro **privado y explícito** de permiso por caso, conforme a [`evalia-publication-approval.schema.json`](../schemas/evalia-publication-approval.schema.json). Cada entrada declara ID, licencia del conjunto, base de autorización y referencia de evidencia. Debe tener el SHA-256 de bytes exactos del conjunto y de la comparación. El programa comprueba correspondencia, unicidad, estado `reviewed`, `redistribution_allowed=true`, licencia y base declarada; el registro de una persona es necesario para verificar el permiso real. Ni `redistribution_allowed=true` ni `LicenseRef-EvalIA-Original` conceden derechos por sí solos.

Después de realizar esa revisión de permisos, guardar el registro bajo `work/` y ejecutar:

```powershell
evalia export-public --dataset datasets/benchmark-v1.jsonl --prompt prompts/extraction-v1.json --base-run runs/5-3-b-qwen3-20261015 --candidate-run runs/5-3-c-qwen25-20261015 --comparison work/6-c-comparison-20261016-final.json --approval work/6-d-permission-review.json --output work/6-d-public-candidate.json
```

El registro usa esta forma; los valores de ejemplo **no son una aprobación**:

```json
{
  "schema_version": "0.1.0",
  "dataset_sha256": "<SHA-256 de bytes del conjunto>",
  "comparison_sha256": "<SHA-256 de bytes de la comparación>",
  "reviewed_at": "<fecha UTC ISO 8601>",
  "reviewer": "<persona que verificó los permisos>",
  "cases": [
    {
      "case_id": "bench-001",
      "source_license": "LicenseRef-EvalIA-Original",
      "basis": "original_created_for_project",
      "evidence_reference": "<registro comprobado de creación y permiso>"
    }
  ]
}
```

El ejemplo es ilustrativo y no valida contra el esquema hasta completar los marcadores. Para cada caso seleccionado se debe consignar una entrada; las demás no saldrán. Las agregaciones `dev` y `test` se recalculan solo sobre la selección, con errores visibles y tiempos descriptivos. Una predicción inválida se representa como `null`, sin copiar su respuesta cruda; `student_required=false` sigue siendo distinto de `null`. El candidato queda marcado `pending_artifact_review` y solo se puede guardar dentro de una ruta privada del repositorio, como `work/`, o fuera del checkout. Nunca se sobrescribe un archivo existente.

En **6.d** se verificó mecánicamente el rechazo de la pareja real al faltar el registro de permisos: no se escribió candidato. En **6.e** corresponde efectuar y registrar la revisión humana de permisos y respaldo semántico, generar el candidato real, inspeccionar manualmente cada campo del JSON y decidir si se publica. No se debe copiar el candidato a `examples/results/` ni a una demo antes de esa puerta.
