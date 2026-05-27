Este repositorio se centra en el caso Fintech de la Evaluación Parcial N°2. La fuente principal para trabajar es [IA_Proyecto/data/raw/fintech_raw.csv](IA_Proyecto/data/raw/fintech_raw.csv), que contiene transacciones con trazabilidad por hash, saldos antes y después, código regulatorio y metadatos de auditoría.

Para ejecutar el flujo principal:

```bash
python pipeline.py
```

El pipeline realiza tres etapas:

1. Ingesta del CSV de transacciones.
2. Transformación de tipos y derivación de métricas de auditoría.
3. Validación estructural y semántica de la cadena de datos.

La configuración del archivo [config.json](config.json) ya apunta al raw del proyecto y puede cambiarse si fuera necesario.

**Pruebas locales y stubs (archivos_test)**

Hemos añadido stubs de prueba dentro del paquete `archivos_test` para poder ejecutar el pipeline sin restaurar las implementaciones externas. Los ficheros de prueba principales son:

- `archivos_test/leer_batch.py` — stub para `leer_datos_batch` (batch de libros).
- `archivos_test/fuente_realtime.py` — stub para `leer_clima_tiempo_real` (snapshots).
- `archivos_test/run_pipeline_test.py` — pequeño runner para validar todo usando los stubs.
- `archivos_test/test.ipynb` — notebook de prueba (migrado desde `archivos test/test.ipynb`).

Comportamiento: si el pipeline no encuentra `ingestion.leer_batch` o `ingestion.fuente_realtime`, intentará usar los stubs en `archivos_test` como fallback — útil solo para pruebas locales.

Comandos recomendados para pruebas (cópialos y ejecútalos en tu máquina local):

```bash
# Crear rama para pruebas (recomendado)
git checkout -b feat/test-stubs

# Añadir cambios y commitear
git add pipeline.py archivos_test/*
git commit -m "test: añadir stubs en archivos_test y selector CLI en pipeline.py para pruebas locales"
git push -u origin feat/test-stubs

# Instalar dependencias si es necesario
python3 -m pip install -r requirements.txt

# Ejecutar solo la fuente CSV
python3 pipeline.py --sources csv

# Ejecutar CSV + batch + realtime (usará stubs si faltan los módulos reales)
python3 pipeline.py --sources csv,batch,realtime

# Ejecutar el script de prueba que resume resultados
python3 -m archivos_test.run_pipeline_test
```

Notas y buenas prácticas:
- Los stubs están pensados solo para pruebas locales y no deben fusionarse a `main` sin revisión. Manténlos en una rama de pruebas y abre un PR con la etiqueta `test` si quieres compartirlos.
- Para mayor seguridad, se puede añadir un flag `--test` o `use_test_stubs` en `config.json` para activar stubs explícitamente; actualmente el pipeline usa fallback implícito.
- Si vas a ejecutar en un entorno CI o producción, asegúrate de restaurar o implementar las versiones reales de `ingestion/leer_batch.py` y `ingestion/fuente_realtime.py`.

Si quieres que añada la nota al PR template o que implemente `--test` ahora, dime y lo hago.


