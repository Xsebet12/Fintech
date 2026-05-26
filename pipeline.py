import json
import os

import pandas as pd

from ingestion.lectura_csv import leer_datos_csv
from procesamiento.transformacion import generar_transformaciones
from data_quality.validacion import ejecutar_validaciones


def load_config(path: str = 'config.json'):
    if not os.path.exists(path):
        print(f'Config file not found: {path} — using defaults')
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_orchestator(config_path: str = 'config.json'):
    config = load_config(config_path)

    almacen_datos = {}

    print("--- Lectura de transacciones fintech")
    fintech_path = config.get('fintech_path', 'fintech.csv')
    almacen_datos['Fintech'] = leer_datos_csv(fintech_path)

    print("--- Resumen de datos sin transformar")
    for elemento, df in almacen_datos.items():
        print(f"\nFUENTE: {elemento}")
        if hasattr(df, 'empty') and not df.empty:
            print(f"Rows: {len(df)} | Columns: {list(df.columns)}")
            print(df.head(2))
        else:
            print("Empty Table (Check connection)")

    almacen_datos = generar_transformaciones(almacen_datos)

    print("\n--- Resumen de datos transformados")
    for elemento, df in almacen_datos.items():
        print(f"FUENTE/TRANSFORMACIÓN: {elemento}")
        if hasattr(df, 'empty') and not df.empty:
            print(df.head(2) if hasattr(df, 'head') else df)
        elif isinstance(df, pd.Series):
            print(df)
        else:
            print("Sin datos o formato no reconocido")

    almacen_datos = ejecutar_validaciones(almacen_datos)

    print("\n--- Resumen de datos validados")
    for elemento, df in almacen_datos.items():
        print(f"FUENTE/VALIDACIÓN: {elemento}")
        if hasattr(df, 'empty') and not df.empty:
            print(df.head(2) if hasattr(df, 'head') else df)
        elif isinstance(df, pd.Series):
            print(df)
        else:
            print("Sin datos o formato no reconocido")

    return almacen_datos


if __name__ == "__main__":
    results = run_orchestator()

