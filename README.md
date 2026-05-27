# Fintech ETL

Proyecto de datos para la Evaluación Parcial N°2 del caso Fintech.

La fuente principal es [IA_Proyecto/data/raw/fintech_raw.csv](IA_Proyecto/data/raw/fintech_raw.csv). Ese archivo contiene transacciones financieras con trazabilidad por `record_hash`, referencia al hash previo, saldos antes y después, código regulatorio y metadatos de auditoría.

## Objetivo

Construir un flujo ETL reproducible para:

1. ingerir transacciones fintech desde CSV,
2. transformar y normalizar los datos,
3. validar consistencia estructural y semántica,
4. generar KPIs de monitoreo,
5. cargar la información en PostgreSQL para análisis y demo.

## Caso de estudio

El caso plantea un sistema de auditoría para una fintech que necesita:

- registros trazables,
- consistencia histórica,
- validación de cadena de hashes,
- separación entre registros válidos e inválidos,
- soporte para reportes regulatorios mensuales.

La solución del proyecto cubre esos requisitos con ingesta, transformación, validación, métricas y persistencia en base de datos.

## Tecnologías

- Python
- pandas
- Jupyter Notebook
- PostgreSQL
- SQLAlchemy
- psycopg2-binary
- python-dotenv

## Flujo del proyecto

El pipeline principal está en [pipeline.py](pipeline.py) y ejecuta estas etapas:

1. Ingesta del CSV.
2. Limpieza y transformación de tipos.
3. Validación estructural y semántica.
4. Cálculo de KPIs y carga de resultados.

Los resultados intermedios se guardan en:

- `IA_Proyecto/data/processed/`
- `IA_Proyecto/data/kpi/`
- `IA_Proyecto/data/metadata/`

## Carga a PostgreSQL

La carga oficial a base de datos está definida en [Script Postgrest.sql](Script%20Postgrest.sql).

Ese script crea:

- `fintech.accounts` para normalizar `account_id`,
- `fintech.transactions` para las transacciones,
- `fintech.kpi_fintech` para el resumen de monitoreo,
- `fintech.stg_transactions` como tabla staging.

La staging se usa para cargar el CSV primero y después insertar los datos normalizados a las tablas finales.

## Notebooks

Los notebooks están organizados por etapa en `IA_Proyecto/notebooks/`:

- `1-Ingesta_fintech.ipynb`
- `2-Transformacion_fintech.ipynb`
- `3-Data_Quality_fintech.ipynb`
- `4-Carga_fintech.ipynb`
- `5-Pipeline_fintech.ipynb`
- `6-Carga_base_datos.ipynb`

El notebook [IA_Proyecto/notebooks/6-Carga_base_datos.ipynb](IA_Proyecto/notebooks/6-Carga_base_datos.ipynb) se usa como apoyo de demostración. El script SQL es la forma más clara de cargar la base de datos de forma reproducible.

## Requisitos

Instalar dependencias:

```bash
python -m pip install -r requirements.txt
```

Si quieres usar PostgreSQL localmente, prepara también un archivo `.env` con estas variables:

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fintech
DB_USER=postgres
DB_PASSWORD=tu_password
```

## Uso

### 1. Ejecutar el ETL principal

```bash
python pipeline.py
```

### 2. Cargar la base de datos

```bash
psql -h localhost -U postgres -d fintech -f "Script Postgrest.sql"
```

### 3. Ejecutar el notebook de carga

Abre [IA_Proyecto/notebooks/6-Carga_base_datos.ipynb](IA_Proyecto/notebooks/6-Carga_base_datos.ipynb) si quieres revisar la carga paso a paso y mostrarla en la defensa.

## KPIs principales

El proyecto calcula y/o expone estos indicadores:

- `total_registros`
- `registros_validos`
- `registros_invalidos`
- `tasa_registros_validos`
- `monto_total_valido`
- `monto_promedio_valido`
- `saldo_promedio_final`
- `transacciones_confirmadas`
- `cuentas_unicas`
- `meses_unicos`

## Archivos clave

- [pipeline.py](pipeline.py) para la ejecución del ETL.
- [ingestion/lectura_csv.py](ingestion/lectura_csv.py) para ingesta y metadata.
- [procesamiento/transformacion.py](procesamiento/transformacion.py) para limpieza y derivaciones.
- [data_quality/validacion.py](data_quality/validacion.py) para validaciones.
- [reporting/kpi.py](reporting/kpi.py) para KPIs.
- [carga/carga_datos.py](carga/carga_datos.py) para persistencia de archivos versionados.
- [Script Postgrest.sql](Script%20Postgrest.sql) para PostgreSQL.

## Salidas esperadas

Al terminar el pipeline deberías obtener:

- CSV versionados de válidos e inválidos en `IA_Proyecto/data/processed/`:
	- `fintech_limpio_*.csv` para los registros válidos,
	- `fintech_invalidos_*.csv` para los registros rechazados,
- CSV versionado del KPI en `IA_Proyecto/data/kpi/` con nombre `kpi_fintech_*.csv`,
- metadata JSON en `IA_Proyecto/data/metadata/`,
- tablas PostgreSQL cargadas desde el script SQL.

En el notebook [pipeline_fintech.ipynb](pipeline_fintech.ipynb) el KPI se muestra en la salida de la celda `resultado['kpis']`, y el resumen de carga a PostgreSQL en `resultado['postgres']`.

## Notas

- El proyecto usa `status = COMPLETED` como estado exitoso de transacción.
- La carga a PostgreSQL debe hacerse con el script SQL para mantener el esquema y la staging.
- Los notebooks quedan como apoyo pedagógico y de demo.


