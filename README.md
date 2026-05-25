

Este repositorio sirve como plantilla mínima para un pipeline ETL de ejemplo. Cambia los parámetros en `config.json` para usar tus propios datasets o fuentes externas sin editar el código fuente:

- `titanic_path`: ruta al CSV local para la ingesta principal.
- `openlibrary.subject` y `openlibrary.limit`: parámetros para `leer_batch`.
- `open_meteo` settings: `latitude`, `longitude`, `snapshots`, `timeout`.

Para ejecutar el pipeline:

```bash
python pipeline.py
```

Flujo de auditoría
------------------

- Cada ingesta guarda metadata en `IA_Proyecto/data/metadata/`.
- Las salidas de `processed` quedan versionadas por timestamp, sin sobrescribir archivos anteriores.
- Los notebooks consumen la última versión disponible para mantener trazabilidad.

Carpetas importantes
--------------------

- **__pycache__**: Carpeta generada automáticamente por Python que contiene archivos compilados (.pyc). Estos archivos aceleran la carga de módulos en ejecuciones posteriores. No es necesario versionarla; añádela a `.gitignore` si aún no está.
- **devcontainer**: Configuración para entornos de desarrollo reproducibles en VS Code. Normalmente se encuentra en una carpeta llamada `.devcontainer/` e incluye `devcontainer.json` y un `Dockerfile` o `docker-compose` que instalan dependencias y herramientas para desarrollar en un contenedor.
- **IA_Proyecto**: Carpeta con el proyecto de inteligencia artificial del repositorio. Contiene datos, notebooks, logs y scripts para limpieza, transformación y experimentación. Ver [IA_Proyecto/README.md](IA_Proyecto/README.md) para más detalles.

