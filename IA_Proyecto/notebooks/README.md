# Notebooks

## Función
Esta carpeta contiene notebooks de apoyo para explicar y demostrar el flujo del proyecto paso a paso.

## Uso previsto
- Presentación de etapas del pipeline.
- Demostración de carga y validación.
- Apoyo para defensa o revisión guiada.

## Reglas recomendadas
- No duplicar la lógica principal del proyecto.
- Usar los notebooks para mostrar y ejecutar, no para mantener la lógica definitiva.
- Mantener referencias claras a los módulos reales del ETL.

## Relación con el resto del proyecto
Los notebooks consumen la lógica de `pipeline.py` y de las carpetas `ingestion`, `procesamiento`, `data_quality`, `reporting` y `carga`.