# Contribuir a EvalIA

## Flujo de trabajo

Usamos GitHub Flow, siguiendo la guía `git-workflow` del plugin ECC: una rama corta por subtarea, un commit coherente y un pull request con su propósito y evidencia de verificación. La rama principal es `main`.

El commit de arranque establece la documentación base. Los siguientes cambios se presentan mediante pull requests. Antes de integrar un cambio se revisa el diff y se ejecutan las comprobaciones pertinentes. Las modificaciones a datos de referencia incluyen su motivo y el efecto sobre métricas anteriores.

Nombres de ramas: `docs/step-0-contract`, `data/step-0-seed-cases`, `feat/dataset-validation` o `fix/date-normalization`.

## Commits

Aplicamos Conventional Commits: `tipo(alcance): descripción`. Los tipos principales son `docs`, `feat`, `fix`, `test`, `chore` y `ci`. La descripción indica un cambio concreto; el cuerpo explica el motivo y la verificación cuando aportan contexto.

Ejemplos:

```text
docs(project): registra el plan aprobado
docs(dataset): define el contrato de anotación
test(grading): cubre requisitos ausentes y negados
```

La documentación y los mensajes de commit se redactan en español. Los identificadores de código y las claves de datos usan inglés para facilitar su integración con bibliotecas y proveedores.

## Cambios pequeños y verificables

1. Consultar el plan y las instrucciones de `AGENTS.md`.
2. Definir la subtarea y su criterio de cierre.
3. Cambiar los archivos necesarios, preservando trabajo existente.
4. Verificar el resultado con pruebas o revisión proporcionales al cambio.
5. Actualizar la bitácora y describir en el pull request qué se comprobó.

Para documentación se revisan enlaces, coherencia y diff. Para contratos se comprueban esquema y ejemplos negativos. Para código se ejecutan las pruebas relevantes. Nunca se declara terminada una revisión diferida antes de que haya ocurrido.

Los archivos de secretos, entornos locales y resultados privados se mantienen fuera de Git. Las llamadas a proveedores remotos quedan para la etapa optativa del plan.
