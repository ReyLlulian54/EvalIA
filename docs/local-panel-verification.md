# Verificación local del panel — 7.d

La prueba manual se realizó el 24 de octubre de 2026 desde el navegador, sobre `main` en el commit `c3a6a66faf8b7947c5eaee5d82050a165b0dc191` y la rama de entrega `codex/evalia-7-d-verificacion`. Se aplicaron las guías ECC `git-workflow`, `contract-first` y `eval-harness`. El [protocolo 7.a](local-panel-protocol.md) fijó entradas y criterios antes de esta corrida. Los artefactos permanecen en `runs/panel/`, ignorado por Git; este documento no publica respuestas ni el informe privado.

## Preparación y escucha

Se comprobó que la PR #36 de 7.c estaba integrada en `main`. `check_benchmark_v1.py` confirmó 36 casos y SHA-256 con saltos LF `598740b54573749e6c7eb9007117f39d9fc971c7a1ee93550a44243d22c0926c`; `evalia validate` aceptó el conjunto. La selección preparada en la interfaz fue `bench-001` a `bench-010`, con ocho casos `dev` y dos `test`. La huella de los **bytes del archivo en este checkout Windows** fue `55641ff55409d3951c88a337635ccbb6a131f1f632d9efab50c96961df75536f` por CRLF; no se sustituyó por la huella LF normalizada. El prompt conservó SHA-256 `2535a9c5f6ab590ca356647dc342958a5459f3a2685ab67523db55a9ed37c86e`.

Ollama 0.32.14 tenía `qwen3:8b` instalado con digest `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`. El cliente heredaba `OLLAMA_HOST=0.0.0.0` de otra configuración y no conectó al primer `ollama list`; se corrigió **solo en el proceso de comprobación** a `127.0.0.1:11434`. La lectura de listeners antes y después de la corrida mostró únicamente `127.0.0.1:11434` para Ollama y `127.0.0.1:8501` para el panel. No se cambió la configuración permanente, no se descargó un modelo y no hubo servicio remoto ni llamada pagada.

## Recorrido y auditoría

Desde el navegador se revisó el resumen inmutable y se pulsó **Ejecutar** una vez: temperatura 0, máximo 256 tokens, espera de I/O 120 segundos y cero reintentos. El panel mostró el estado final y permitió seleccionar la corrida. El manifiesto 0.3.0 cerró como `completed` con `request_count=10`, `recorded_count=10`, `success_count=10` y `failure_count=0`. Los diez registros conservaron orden e IDs previstos, `attempts=1` y el digest esperado. Una respuesta recibida no acredita contenido correcto.

Se seleccionaron las fuentes originales y se calculó el informe privado con el puntuador existente. El informe fue compatible y se pudo volver a auditar tras recargar la página. El puntuador detectó **dos errores de formato `noncanonical_skill` en respuestas de la partición `test`**; quedaron registrados como errores de salida del modelo, no como fallos de transporte ni del panel. No se modificaron prompt, etiquetas o vocabulario ni se repitió la inferencia para ocultarlos. Su detalle por caso y las métricas quedan solo en el informe privado. La observación no constituye una nueva comparación de modelos ni autoriza exportación.

Se cambió el filtro de registros, se recargó la página y se volvió a consultar la corrida y el informe existente. Tras estas acciones seguía habiendo un solo directorio de corrida, `request_count=10` y diez registros. Las huellas SHA-256 de `manifest.json`, `responses.jsonl` y `score-report.json` permanecieron idénticas durante la consulta. La sesión nueva mostró **Sin preparar** y **Ejecutar** deshabilitado, mientras los artefactos seguían consultables. Estos hechos cubren P13 y P14 del protocolo para esta sesión local; las pruebas simuladas de 7.b y 7.c cubren los otros escenarios declarados allí.

## Reproducción y límites

Desde PowerShell en la raíz del repositorio, con el extra `panel` instalado, comprobar el modelo y la escucha antes de inferir:

```powershell
$env:OLLAMA_HOST = '127.0.0.1:11434'
ollama list
Get-NetTCPConnection -State Listen -LocalPort 11434 |
    Select-Object LocalAddress,LocalPort,OwningProcess
.\.venv\Scripts\python scripts\run_local_panel.py
```

El lanzador permanece activo en esa terminal. En otra, repetir `Get-NetTCPConnection -State Listen -LocalPort 11434,8501 | Select-Object LocalAddress,LocalPort,OwningProcess` y comprobar que ambos puertos muestran solo `127.0.0.1`. Si Ollama no está en ejecución, abrir otra terminal y ejecutar `$env:OLLAMA_HOST = '127.0.0.1:11434'` seguido de `ollama serve`; comprobar de nuevo su listener. Si falta `qwen3:8b`, descargarlo de forma deliberada con `ollama pull qwen3:8b` antes de la prueba; el panel no lo hace. Los artefactos reales permanecen privados bajo `runs/panel/`; no incluirlos en Git ni en la demo. Los tiempos y el formato de las respuestas dependen de esta máquina, de Ollama y del digest observado. El siguiente paso del plan es **8, demo pública de solo lectura**, con sus propias puertas de publicación.
