from __future__ import annotations

import logging
import json
import os
import traceback
from pathlib import Path

import pandas as pd

from IA_Proyecto.src.audit_utils import ensure_dir, utc_now_iso
from carga.carga_datos import cargar_datos
from carga.carga_postgres import load_to_postgres
from data_quality.validacion import ejecutar_validaciones
from ingestion.lectura_csv import leer_datos_csv
from procesamiento.transformacion import generar_transformaciones
from reporting.kpi import calcular_kpis


logger = logging.getLogger(__name__)


def _setup_logging(logs_dir: str | Path):
    log_path = ensure_dir(logs_dir) / 'pipeline_etl.log'
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        root_logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')

        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        root_logger.addHandler(stream_handler)

    return log_path


def _save_pipeline_status(kpi_dir: str | Path, status: str, postgres_status: str, postgres_error: str | None = None):
    status_path = ensure_dir(kpi_dir) / f"pipeline_status_{utc_now_iso().replace(':', '').replace('.', '')}.json"
    payload = {
        'etl_status': status,
        'postgres_status': postgres_status,
        'postgres_error': postgres_error,
        'timestamp': utc_now_iso(),
    }
    with open(status_path, 'w', encoding='utf-8') as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
    return status_path


def load_config(path: str = 'config.json') -> dict:
    if not os.path.exists(path):
        print(f'Config file not found: {path} — using defaults')
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _print_dataframe_summary(title: str, df: pd.DataFrame):
    print(title)
    if isinstance(df, pd.DataFrame) and not df.empty:
        print(f"Rows: {len(df)} | Columns: {list(df.columns)}")
        print(df.head(2))
    else:
        print("Empty Table (Check connection)")


def run_pipeline(config_path: str = 'config.json'):
    config = load_config(config_path)

    fintech_path = config.get('fintech_path', 'IA_Proyecto/data/raw/fintech_raw.csv')
    output_dirs = config.get('output_dirs', {})
    processed_dir = ensure_dir(output_dirs.get('processed', 'IA_Proyecto/data/processed'))
    kpi_dir = ensure_dir(output_dirs.get('kpi', 'IA_Proyecto/data/kpi'))
    logs_dir = ensure_dir(output_dirs.get('logs', 'IA_Proyecto/logs'))

    log_path = _setup_logging(logs_dir)
    logger.info('Pipeline iniciado. Log activo en %s', log_path)

    almacen_datos = {}

    print("--- Etapa 1: Ingesta")
    almacen_datos['Fintech'] = leer_datos_csv(fintech_path)
    _print_dataframe_summary("--- Resumen de datos ingeridos", almacen_datos['Fintech'])

    print("\n--- Etapa 2: Limpieza y transformación")
    almacen_datos = generar_transformaciones(almacen_datos)
    for elemento, df in almacen_datos.items():
        if isinstance(df, pd.DataFrame):
            _print_dataframe_summary(f"FUENTE/TRANSFORMACIÓN: {elemento}", df)

    print("\n--- Etapa 3: Validación")
    almacen_datos = ejecutar_validaciones(almacen_datos, config=config)
    for elemento in ['Fintech', 'Fintech Validos', 'Fintech Invalidos']:
        df = almacen_datos.get(elemento)
        if isinstance(df, pd.DataFrame):
            _print_dataframe_summary(f"FUENTE/VALIDACIÓN: {elemento}", df)

    print("\n--- Etapa 4: KPI y carga")
    kpi_df = calcular_kpis(almacen_datos)
    print(kpi_df)

    resultados_carga = cargar_datos(almacen_datos, kpi_df, output_dirs=output_dirs)
    print("\n--- Etapa 5: Carga a PostgreSQL")
    resultados_postgres = {}
    postgres_status = 'success'
    postgres_error = None
    try:
        resultados_postgres = load_to_postgres(almacen_datos, kpi_df)
    except Exception as exc:
        postgres_status = 'failed'
        postgres_error = f'{exc.__class__.__name__}: {exc}'
        logger.exception('Fallo la carga a PostgreSQL')
        print(f"\n--- Carga a PostgreSQL fallida: {postgres_error}")
    finally:
        _save_pipeline_status(kpi_dir, 'success', postgres_status, postgres_error)
    print("\n--- Artefactos guardados")
    if resultados_carga:
        for nombre, paths in resultados_carga.items():
            csv_path, metadata_path = paths
            print(f"{nombre}: {csv_path}")
            if metadata_path is not None:
                print(f"metadata: {metadata_path}")
    else:
        print("No se generaron artefactos para guardar.")

    print("\n--- Resumen de carga PostgreSQL")
    if resultados_postgres:
        for nombre, total in resultados_postgres.items():
            print(f"{nombre}: {total} registros")
    else:
        print("La carga a PostgreSQL no se completó, pero el ETL principal terminó correctamente.")

    return {
        'datos': almacen_datos,
        'kpis': kpi_df,
        'carga': resultados_carga,
        'postgres': resultados_postgres,
        'postgres_status': postgres_status,
        'postgres_error': postgres_error,
        'log_path': str(log_path),
    }


if __name__ == '__main__':
    run_pipeline()

