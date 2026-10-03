# EvalIA

Evaluación reproducible de modelos y prompts en español. El objetivo es comparar salidas con respuestas revisadas y mostrar aciertos, errores, evidencia, tiempo y costo bajo condiciones documentadas.

## Estado del proyecto

Proyecto en etapa inicial. El plan fue aprobado el 3 de octubre de 2026. Ya existe un contrato de datos y diez casos ficticios con anotaciones iniciales, pendientes de revisión diferida. Los comandos de evaluación y los paneles descritos en el plan son entregables futuros.

La primera tarea será extraer fecha de cierre, modalidad, habilidades obligatorias y requisito de ser estudiante de fragmentos de convocatorias. La primera versión usará Ollama localmente, tendrá una interfaz web local para ejecutar experimentos y una demo pública de resultados precomputados.

## Documentación

- [Plan de implementación](plans/evalia-implementation.md): alcance, secuencia, dependencias y criterios de cierre.
- [Bitácora](docs/progress.md): subtareas realizadas, verificaciones y siguiente trabajo.
- [Modo de contribución](CONTRIBUTING.md): ramas, commits y revisión de cambios.
- [Guía de anotación](docs/annotation-guide.md): significado de los campos y reglas de evidencia.
- [Contrato de casos](schemas/evalia-case.schema.json): estructura autoritativa del formato 0.1.0.
- [Casos de arranque](datasets/README.md): diez ejemplos ficticios, decisiones de anotación y estado de revisión.

## Desarrollo

El trabajo avanza en subtareas pequeñas. Cada entrega conserva su verificación y describe las decisiones necesarias para continuar en otra sesión. El repositorio seguirá las guías relevantes del plugin ECC instalado en el entorno de desarrollo.

La licencia de distribución se definirá en el paso de configuración del paquete. La publicación del repositorio no constituye una autorización de reutilización de textos de terceros.
