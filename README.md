# mi-ide-cloud
Test Gestión datos IA

Template usage
--------------

Este repositorio sirve como plantilla mínima para un pipeline ETL de ejemplo. Cambia los parámetros en `config.json` para usar tus propios datasets o fuentes externas sin editar el código fuente:

- `titanic_path`: ruta al CSV local para la ingesta principal.
- `openlibrary.subject` y `openlibrary.limit`: parámetros para `leer_batch`.
- `open_meteo` settings: `latitude`, `longitude`, `snapshots`, `timeout`.

Para ejecutar el pipeline:

```bash
python pipeline.py
```

