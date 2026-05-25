import pandas as pd
import time
import json
import os

from ingestion.lectura_csv import leer_datos_csv
from ingestion.leer_batch import leer_datos_batch
from ingestion.fuente_realtime import leer_clima_tiempo_real
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

    print("--- Lectura de csv")
    titanic_path = config.get('titanic_path', 'Titanic.csv')
    almacen_datos['Titanic'] = leer_datos_csv(titanic_path)

    print("--- Lectura de titulos libros")
    ol_conf = config.get('openlibrary', {})
    subject = ol_conf.get('subject', 'scifi')
    limit = ol_conf.get('limit', 10)
    almacen_datos['Libros'] = leer_datos_batch(subject=subject, limit=limit)

    print("--- Lectura del clima en tiempo real")
    total_lecturas = []
    om_conf = config.get('open_meteo', {})
    snapshots = om_conf.get('snapshots', 5)
    lat = om_conf.get('latitude', -33.453654)
    lon = om_conf.get('longitude', -70.573846)
    timeout = om_conf.get('timeout', 5)

    for i in range(int(snapshots)):
        print(f"  > instantanea {i+1}...")
        df_snap = leer_clima_tiempo_real(latitude=lat, longitude=lon, timeout=timeout)
        if not df_snap.empty:
            total_lecturas.append(df_snap)
        time.sleep(1)

    if total_lecturas:
        almacen_datos['clima'] = pd.concat(total_lecturas, ignore_index=True)
    else:
        almacen_datos['clima'] = pd.DataFrame()

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

