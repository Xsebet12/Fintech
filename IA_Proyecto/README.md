IA_Proyecto — Estructura y propósito
----------------------------------

Esta carpeta contiene los datos, notebooks y artefactos asociados al desarrollo y experimentación de modelos de inteligencia artificial para este proyecto.

Estructura
```
IA_Proyecto/
├── data/
│   ├── raw/         # Datos originales sin modificar (ingesta)
│   └── processed/   # Datos ya limpiados y transformados, listos para entrenamiento
├── logs/            # Registros de ejecución y métricas de entrenamiento/validación
├── notebooks/       # Notebooks Jupyter para exploración, validación y pipelines
└── src/             # Código/funciones reutilizables (preprocesado, modelos, utilidades)
```

Descripción de carpetas
- `data/raw/`: Guarda los archivos tal cual se descargan o reciben. Mantén aquí los originales para reproducibilidad.
- `data/processed/`: Resultados de las tareas de limpieza y transformación. Versiona solo cuando sea necesario (o guarda hashes) para no ocupar espacio innecesario.
- `logs/`: Archivos de logs y resultados de experimentos. Útil para comparar ejecuciones y depurar problemas.
- `notebooks/`: Incluye notebooks como `1-Notebook_gestion_datos.ipynb` (gestión y limpieza), `2-Validacion_estructural_semantica.ipynb` (validaciones) y `3-Carga_base_datos.ipynb` (carga a BD). Usa estos notebooks para explorar y reproducir pasos de preprocesado.
- `src/`: Coloca funciones y módulos que quieras importar desde los notebooks o scripts. Mantén la lógica reutilizable aquí para evitar duplicación.

Buenas prácticas
- No modifiques los archivos en `data/raw/` directamente; crea scripts en `src/` que produzcan `data/processed/`.
- Añade `data/` y `logs/` a `.gitignore` si contienen datos sensibles o pesados; versiona solo muestras o metadatos relevantes.
- Documenta en esta README cualquier paso de preprocesado crítico o dependencias especiales.

Si quieres, puedo añadir comandos concretos para ejecutar los notebooks en un entorno `devcontainer` o ejemplos de scripts en `src/`.

