Este repositorio se centra en el caso Fintech de la Evaluación Parcial N°2. La fuente principal es [fintech.csv](fintech.csv), que contiene transacciones con trazabilidad por hash, saldos antes y después, código regulatorio y metadatos de auditoría.

Para ejecutar el flujo principal:

```bash
python pipeline.py
```

El pipeline realiza tres etapas:

1. Ingesta del CSV de transacciones.
2. Transformación de tipos y derivación de métricas de auditoría.
3. Validación estructural y semántica de la cadena de datos.

La configuración del archivo [config.json](config.json) permite cambiar la ruta del CSV si fuera necesario.

