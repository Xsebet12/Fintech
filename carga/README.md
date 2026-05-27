# Carga

## Función
Esta carpeta contiene la persistencia de los resultados del proyecto.

## Archivos principales
- `carga_datos.py`: guarda CSV versionados de válidos, inválidos y KPIs.
- `carga_postgres.py`: carga los datos a PostgreSQL usando variables de entorno en `db.env`.

## Entradas
- `Fintech Validos`
- `Fintech Invalidos`
- `kpi_df`

## Salidas
- CSV versionados en `IA_Proyecto/data/processed/` y `IA_Proyecto/data/kpi/`
- Tablas en PostgreSQL cuando la conexión está disponible

## Uso
Se ejecuta al final del pipeline. La persistencia en archivos es la salida mínima esperada; la carga a PostgreSQL es un paso adicional de demostración y explotación.