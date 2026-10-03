# Instrucciones de trabajo para EvalIA

- Consultar `plans/evalia-implementation.md` y `docs/progress.md` antes de continuar.
- Usar las guías pertinentes del plugin ECC disponible en el entorno. Para Git y documentación de contratos, aplicar `git-workflow` y `contract-first`; para implementar evaluaciones, aplicar `eval-harness`.
- Avanzar una subtarea concreta por entrega. Registrar qué quedó terminado y qué sigue; no implementar etapas posteriores por iniciativa propia.
- Mantener commits Conventional Commits en español y ramas cortas con pull requests. Revisar cambios y evidencias antes de integrar.
- Mantener una fuente autoritativa para el contrato de datos. Los consumidores y ejemplos deben cumplirla.
- Distinguir valores desconocidos (`null`) de negativas explícitas (`false`), y citas literales de respaldo semántico.
- No atribuir resultados de modelos, usuarios o calidad de producción sin evidencia registrada.
- Ejecutar verificaciones proporcionales al cambio. No efectuar llamadas pagadas en CI.
- Preservar archivos del usuario y excluir secretos y resultados privados del repositorio.
- No marcar como completa una revisión diferida de datos hasta haberla realizado. No crear memoria del usuario salvo solicitud explícita.
