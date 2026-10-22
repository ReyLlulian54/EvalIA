# Interfaz Streamlit del panel local — 7.c

El panel permite preparar una selección, ejecutarla mediante un botón separado y consultar sus artefactos privados. Reutiliza el [controlador 7.b](local-panel-controller.md), sus [tipos compartidos](../src/evalia/panel/types.py) y los esquemas existentes. No modifica la rúbrica ni publica resultados.

## Instalación y arranque

Desde la raíz del checkout, con Python 3.11 o posterior:

```powershell
.\.venv\Scripts\python -m pip install -e ".[dev,panel]"
.\.venv\Scripts\python scripts\run_local_panel.py
```

Abrir <http://127.0.0.1:8501>. Para detener el servidor, pulsar Ctrl+C en la terminal. El extra `panel` instala Streamlit; la CLI y el controlador siguen funcionando sin esa dependencia. Para un uso sin herramientas de desarrollo basta instalar `.[panel]`. Si el entorno no tiene pip, usar `python -m pip --python .venv install -e ".[dev,panel]"`.

El [lanzador](../scripts/run_local_panel.py) obtiene la raíz desde su ubicación y utiliza el mismo intérprete. Fija por argumentos de mayor precedencia `server.address=127.0.0.1`, puerto 8501, CORS y XSRF activos y estadísticas desactivadas, incluso si existe una configuración global distinta. Oculta las opciones de despliegue y trazas de la barra integrada de Streamlit. Desactiva la vigilancia de archivos y la ejecución al guardar para evitar recargas del código durante una corrida. No acepta argumentos que cambien estos valores. El modo soportado es un solo proceso; si el puerto está ocupado, detener el panel anterior antes de iniciar otro.

No se necesita Ollama para abrir, preparar, consultar artefactos o ejecutar las pruebas simuladas. Para inferencia se necesita el servidor local y el nombre exacto de un modelo ya descargado. El panel usa `http://127.0.0.1:11434`, sin heredar `OLLAMA_HOST`, descargar modelos ni iniciar servicios. Antes de **7.d** se comprobará dónde escucha Ollama y se verificará el modelo; no basta con que el cliente use una URL local.

## Recorrido

1. Elegir conjunto, prompt y parámetros. **Preparar ejecución** valida las entradas y muestra IDs, splits, hashes, parámetros y destino. Enter solo envía este formulario: no inicia inferencia.
2. Revisar el resumen y pulsar **Ejecutar**. El resumen preparado determina lo que se envía; cambios no preparados no alteran esa selección. La intención se consume antes de llamar al motor, incluso si la ejecución falla. Para repetir deliberadamente hay que preparar de nuevo.
3. Consultar una corrida y sus casos. Cambiar selecciones o filtros no ejecuta modelos. Los conteos distinguen respuestas de proveedor de calidad del contenido. Una corrida sin cierre confirmado conserva su estado y sus archivos.
4. Seleccionar las fuentes originales para auditar la puntuación. **Calcular métricas** es una acción explícita; leer un informe existente no crea ni sobrescribe archivos. El puntuador admite el prompt congelado y splits `dev`/`test`; otras entradas muestran la incompatibilidad sin provocar otra inferencia.

La selección y el controlador se conservan en la sesión de Streamlit. Recargar completamente o abrir otra pestaña crea una sesión sin orden pendiente; los artefactos siguen consultables. Cerrar el navegador no garantiza cancelar una solicitud. Una sola ejecución activa por proceso está protegida por el controlador, incluso entre sesiones.

## Privacidad e interpretación

Los artefactos quedan en `runs/panel/`, ignorado por Git. Por defecto se muestran identificadores, conteos y códigos. La respuesta cruda requiere una consulta explícita y se representa literalmente. No hay publicación ni descarga de respuestas privadas desde el panel.

Las métricas conservan numeradores y denominadores, separan `dev` de `test` y no asignan un ganador. Un denominador cero se muestra como **No aplicable**; uso o costo ausente, **No informado**. Las etiquetas distinguen `null` (**Desconocido**) de `false` (**No**). Las citas que el prompt no pidió mantienen `not_observed`; no acreditan respaldo semántico. Los tiempos corresponden a la máquina y corrida consultadas.

## Verificación y límites

Las pruebas de interacción usan `streamlit.testing.v1.AppTest`, el controlador y motor reales con un proveedor simulado y conexiones bloqueadas. Ejecutarlas con el extra `panel` instalado:

```powershell
.\.venv\Scripts\python -m pytest tests\panel
.\.venv\Scripts\ruff check .
```

La [bitácora](progress.md) registra las versiones efectivamente probadas, los resultados de las pruebas y la revisión visual. El recorrido real con diez casos, la auditoría de solicitudes y la comprobación de escucha de Ollama siguen en **7.d**. La demo pública corresponde al paso 8.

Referencias oficiales consultadas mediante Context7: [formularios](https://docs.streamlit.io/develop/concepts/architecture/forms), [Session State](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state), [AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest) y [precedencia de configuración](https://docs.streamlit.io/develop/concepts/configuration/options).
