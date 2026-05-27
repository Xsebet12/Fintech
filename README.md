Este repositorio se centra en el caso Fintech de la Evaluación Parcial N°2. La fuente principal para trabajar es [IA_Proyecto/data/raw/fintech_raw.csv](IA_Proyecto/data/raw/fintech_raw.csv), que contiene transacciones con trazabilidad por hash, saldos antes y después, código regulatorio y metadatos de auditoría.

El objetivo del proyecto es aplicar un flujo **ETL** sobre los datos de transacciones y, una vez limpios y validados, calcular **KPIs** de monitoreo para la demo y la defensa del caso.

Para ejecutar el flujo principal:

```bash
python pipeline.py
```

El pipeline realiza cuatro etapas:

1. Ingesta del CSV de transacciones.
2. Transformación de tipos y derivación de métricas de auditoría.
3. Validación estructural y semántica de la cadena de datos.
4. Carga de los datos limpios y generación de KPIs.

La configuración del archivo [config.json](config.json) ya apunta al raw del proyecto y puede cambiarse si fuera necesario.

### Salidas generadas

El pipeline guarda los datos limpios en `IA_Proyecto/data/processed/` y los KPIs en `IA_Proyecto/data/kpi/`, además de sus metadatos versionados en la carpeta `metadata` asociada.

### Notebooks del proyecto

Los notebooks del caso quedaron organizados por etapa dentro de `IA_Proyecto/notebooks/`:

- `1-Ingesta_fintech.ipynb`
- `2-Transformacion_fintech.ipynb`
- `3-Data_Quality_fintech.ipynb`
- `4-Carga_fintech.ipynb`

En la raíz del repositorio queda también el notebook de ejecución sencilla:

- `pipeline_fintech.ipynb`

La carga de resultados se documenta en notebook, pero la lógica reusable está implementada en `carga/carga_datos.py` para que el pipeline y la demo la invoquen sin duplicar código.

### KPI sugeridos para la demo

- `tasa_registros_validos`: proporción de transacciones que pasan la validación.
- `monto_total_valido`: suma de los montos válidos.
- `monto_promedio_valido`: ticket promedio.
- `saldo_promedio_final`: saldo posterior promedio.
- `transacciones_confirmadas`: número de transacciones con estado confirmado.
- `cuentas_unicas`: cantidad de cuentas distintas procesadas.

### Pruebas locales

```bash
python3 -m pip install -r requirements.txt
python3 pipeline.py
```

Si luego quieres extender la demo, la siguiente mejora natural es añadir gráficos de KPI y una pequeña bitácora de ejecución por fecha.


