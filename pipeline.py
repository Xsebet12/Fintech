from __future__ import annotations

import json
import os

import pandas as pd

from IA_Proyecto.src.audit_utils import ensure_dir
from carga.carga_datos import cargar_datos
from data_quality.validacion import ejecutar_validaciones
from ingestion.lectura_csv import leer_datos_csv
from procesamiento.transformacion import generar_transformaciones
from reporting.kpi import calcular_kpis


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
    print("\n--- Artefactos guardados")
    if resultados_carga:
        for nombre, paths in resultados_carga.items():
            csv_path, metadata_path = paths
            print(f"{nombre}: {csv_path}")
            if metadata_path is not None:
                print(f"metadata: {metadata_path}")
    else:
        print("No se generaron artefactos para guardar.")

    return {
        'datos': almacen_datos,
        'kpis': kpi_df,
        'carga': resultados_carga,
    }


if __name__ == '__main__':
    run_pipeline()

