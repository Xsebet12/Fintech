# Ingesta

## Función
Esta carpeta contiene la lógica de entrada de datos del proyecto. Su responsabilidad es leer el archivo fuente, normalizar la primera capa de auditoría y devolver un `DataFrame` listo para transformación.

## Archivo principal
- `lectura_csv.py`: lee el CSV base, genera `record_hash` si falta, agrega marca de tiempo de ingesta y guarda metadata de trazabilidad.

## Entradas
- CSV fuente del proyecto.
- Configuración de ruta cuando se invoca desde `pipeline.py`.

## Salidas
- `DataFrame` con los datos ingeridos.
- Metadata JSON de la ingesta en la carpeta de metadatos.

## Uso
Esta carpeta no se ejecuta sola. La consume `pipeline.py` como primer paso del flujo ETL.