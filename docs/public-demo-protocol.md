# Protocolo de la demo pública — etapa 8

Estado: **8.a y 8.b completas; 8.c en verificación; sigue 8.d**. Este documento fija la fuente, el recorrido y las puertas del visor de solo lectura. La demo presenta una comparación descriptiva ya aprobada; nunca ejecuta modelos ni exporta datos privados. El [recorrido local de 8.b](public-demo-ui.md) registra el arranque y sus límites; la [integración 8.c](public-demo-ci.md), sus pruebas y su CI se revisan por separado.

## Subtareas y puertas

| Subtarea | Entrega | Puerta de salida |
| --- | --- | --- |
| **8.a. Diseño y contrato** | Este protocolo: fuente única, arquitectura, estados, vista, filtros, límites y criterios D01–D12. | Coherencia con el esquema público 0.1.1, el artefacto aprobado, el plan y las guías de despliegue; enlaces y diff revisados. |
| **8.b. Visor de solo lectura** | `app/public_app.py` independiente y lector de ruta fija; resumen por split, filtros y detalle de casos/errores. | Completada: pruebas focalizadas de datos y `AppTest`, rechazo cerrado de artefactos no aprobados, y revisión visual local. |
| **8.c. Integración y CI** | Dependencias reproducibles desde el checkout, instalación limpia y flujo de CI sin proveedor. | En revisión: suite completa, Ruff, aislamiento y arranque local superados; falta la ejecución de GitHub Actions. Las versiones transitivas no están congeladas. |
| **8.d. Publicación** | Revisión final de permisos, configuración del alojamiento, URL y release inicial. | Artefacto/hash y enlaces auditados, licencia del código resuelta, revisión visual en la URL final y autorización para publicar. |

Una entrega y una PR revisables corresponden a cada fila. La 8.c no autoriza desplegar ni comenzar 8.d por iniciativa propia.

## Fuente y límite de confianza

El único contrato de datos es [`evalia-public-report.schema.json`](../schemas/evalia-public-report.schema.json), versión **0.1.1**, validado con Draft 2020-12 y `FormatChecker` por [`public_report_validator()`](../src/evalia/reports/schema.py). El único artefacto seleccionado para esta demo es [`benchmark-v1-qwen3-vs-qwen25.json`](../examples/results/benchmark-v1-qwen3-vs-qwen25.json), SHA-256 de **bytes LF** `7071ee504391a38c9866342481ff5124bdd75199c74189b17e024baf32f22565`. [La revisión 6.e](6-e-review.md) confirmó derechos de los 36 casos, auditó el candidato y seleccionó esta copia con `publication_review=approved_for_publication`; [la prueba existente](../tests/reports/test_public_artifact.py) fija la huella y comprueba que no contiene textos ni respuestas crudas.

Antes de renderizar, el lector debe resolver solo esa ruta constante dentro del checkout, comprobar que es un archivo regular, verificar su SHA-256 de bytes, parsear JSON, validar el esquema y exigir el estado aprobado. Un campo `approved_for_publication` en otro JSON **no** concede permiso para mostrarlo. Ante ausencia, alteración, versión distinta, esquema inválido o aprobación pendiente, mostrar un error seguro y detener la lectura: sin selector de archivos, carga, URL de reporte, ruta por parámetro ni fallback a `runs/` o `work/`. No se consultan los archivos privados de 6.e en la demo.

El punto de entrada público debe ser independiente del [panel local](../app/local_app.py). Puede reutilizar el validador del contrato público, pero no importar `evalia.panel`, `evalia.runner`, `evalia.providers`, `evalia.cli` ni `evalia.reports.export_public`; tampoco instanciar clientes HTTP de inferencia. Los filtros operan únicamente sobre el objeto ya validado en memoria. El despliegue no requiere Ollama, OpenRouter ni claves. La prueba de aislamiento de 8.c bloqueará importaciones y conexiones de inferencia, además de comprobar que `runs/` y `work/` no se leen.

## Recorrido y dirección visual

La audiencia es una persona que evalúa el proyecto y necesita entender **qué se comparó, sobre cuántos casos y dónde falló cada salida**. La dirección visual será técnica, sobria y legible: primer viewport con título, alcance y dos modelos; resumen separado de `dev` y `test`; controles compactos; tabla de casos; detalle de un caso. El dato y sus denominadores tienen prioridad sobre adornos. En pantallas estrechas, los controles y columnas se apilan sin cortar etiquetas; los estados no dependen solo del color.

1. **Contexto:** identificar modelos y digest/procedencia disponibles, 36 casos ficticios seleccionados (`dev` 27, `test` 9), fecha del reporte y límites `selected_cases_only`, `not_observed` y `descriptive_no_winner`. No mostrar un ganador, nota compuesta, costo inventado ni afirmación de calidad de producción. El reporte no contiene textos de convocatoria ni citas de los modelos, así que la vista no puede presentarlos como evidencia.
2. **Resumen:** usar los conteos ya contenidos en `splits.dev` y `splits.test`, con denominadores explícitos para categorías por campo y errores por modelo. No recalcular una nueva métrica global o mezclar splits. Un conteo cero se muestra como cero; una razón sin denominador, si se ofrece, como «No aplicable».
3. **Exploración:** filtrar los `cases` aprobados por split, ID y estado de cada modelo (`scored`, `provider_error`, `internal_error`, `format_error`); permitir encontrar `not_comparable` y categorías por campo. Los filtros cambian solo la vista; los agregados fijados del reporte conservan sus denominadores y se etiquetan como tales. Un filtro sin coincidencias muestra una explicación y una acción para restablecerlo.
4. **Detalle:** mostrar `expected`, predicción base/candidata cuando `status=scored`, categoría de los cuatro campos, tiempos y códigos de error. Para error, `prediction=null` se presenta como «Sin predicción»; `student_required=false` es «No» y `null` es «Desconocido». El estado y el código se leen como datos literales, sin HTML del contenido del artefacto.

Estados previstos: carga local breve sin progreso inventado; éxito con datos; filtro vacío con restablecimiento; error de artefacto que bloquea la vista; y errores parciales de modelos **dentro del reporte válido**, visibles sin bloquear los otros casos. No hay estado de permiso del visitante porque no se solicita autenticación, ni estado de ejecución porque la demo no ejecuta nada.

## Criterios de aceptación

| ID | Comprobación exigida | Entrega |
| --- | --- | --- |
| D01 | Ruta fija, hash de bytes, esquema 0.1.1 y aprobación exigidos antes de mostrar datos. | 8.b–c |
| D02 | Archivo ausente, cambiado, inválido o pendiente: rechazo cerrado y mensaje útil, sin leer otro origen. | 8.b–c |
| D03 | Ninguna lectura de `runs/`/`work/`, carga arbitraria, clave o llamada de inferencia. | 8.b–c |
| D04 | Punto de entrada público no importa motor, proveedor, controlador local ni exportador. | 8.b–c |
| D05 | `dev`/`test` y denominadores del reporte se conservan; sin nota compuesta o ganador. | 8.b–c |
| D06 | Filtros por split, ID, estado y casos no comparables no alteran el artefacto ni los agregados. | 8.b–c |
| D07 | Casos con error muestran estado/código y ausencia de predicción, sin ocultarse. | 8.b–c |
| D08 | `null` y `false` se distinguen; `not_observed` no se convierte en respaldo semántico. | 8.b–c |
| D09 | Pruebas de widgets y contenido con `AppTest`; revisión real en navegador de móvil/escritorio, foco y enlaces. | 8.b–d |
| D10 | Instalación limpia, suite, Ruff y CI sin Ollama ni llamadas pagadas. | 8.c |
| D11 | Artefacto, permisos, licencia del código y URL final revisados antes de publicar. | 8.d |
| D12 | README, plan y bitácora reflejan evidencia y siguiente subtarea en cada entrega. | 8.a–d |

`AppTest` permite probar controles y contenido, pero [Streamlit documenta límites](https://docs.streamlit.io/develop/concepts/app-testing/cheat-sheet) para gráficos, medios y `st.data_editor`; la revisión visual sigue siendo necesaria. En Community Cloud se elige repositorio, rama y punto de entrada; [se ejecuta desde la raíz del repositorio](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization) y [requiere dependencias declaradas](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies). Esto orienta 8.c–d, sin fijar aún el alojamiento ni crear una URL. La licencia del código sigue pendiente; los derechos de publicación de los casos aprobados no la sustituyen.

**Configuración humana:** ninguna para 8.a. Para 8.b–c basta el entorno de desarrollo local existente; no se activa Ollama. Antes de 8.d se debe acordar alojamiento/cuenta, URL y licencia del código, revisar la publicación concreta y sus permisos.
