import json
import os

import pandas as pd

from ingestion.lectura_csv import leer_datos_csv
from procesamiento.transformacion import generar_transformaciones
from data_quality.validacion import ejecutar_validaciones

def run_orchestator_selected(selected, config_path: str = 'config.json'):
    """Ejecuta el orquestador solo para las fuentes indicadas en `selected`.
    `selected` es un conjunto con elementos: 'csv', 'batch', 'realtime'.
    """
    config = load_config(config_path)

    almacen_datos = {}

    if 'csv' in selected:
        print("--- Lectura de transacciones fintech (CSV)")
        fintech_path = config.get('fintech_path', 'IA_Proyecto/data/raw/fintech_raw.csv')
        almacen_datos['Fintech'] = leer_datos_csv(fintech_path)

    if 'batch' in selected:
        print("--- Lectura de datos batch (libros)")
        try:
            from ingestion.leer_batch import leer_datos_batch
            topic = config.get('batch_topic', 'scifi')
            almacen_datos['Libros'] = leer_datos_batch(topic)
        except Exception as exc:
            print(f"No se pudo ejecutar lectura batch desde ingestion: {exc}")
            try:
                from archivos_test.leer_batch import leer_datos_batch as _leer_batch
                topic = config.get('batch_topic', 'scifi')
                almacen_datos['Libros'] = _leer_batch(topic)
                print("Usando stub de prueba para lectura batch (archivos_test.leer_batch)")
            except Exception as exc2:
                print(f"Fallback test stub failed: {exc2}")
                import pandas as _pd
                almacen_datos['Libros'] = _pd.DataFrame()

    if 'realtime' in selected:
        print("--- Lectura del clima en tiempo real (snapshots)")
        try:
            from ingestion.fuente_realtime import leer_clima_tiempo_real
            import time as _time
            total_lecturas = []
            n_snapshots = int(config.get('realtime_snapshots', 5))
            interval = float(config.get('realtime_interval_seconds', 1))
            for i in range(n_snapshots):
                print(f"  > instantanea {i+1}...")
                df_snap = leer_clima_tiempo_real()
                if not df_snap.empty:
                    total_lecturas.append(df_snap)
                _time.sleep(interval)
            if total_lecturas:
                import pandas as _pd
                almacen_datos['clima'] = _pd.concat(total_lecturas, ignore_index=True)
            else:
                import pandas as _pd
                almacen_datos['clima'] = _pd.DataFrame()
        except Exception as exc:
            print(f"No se pudo ejecutar lectura realtime desde ingestion: {exc}")
            try:
                from archivos_test.fuente_realtime import leer_clima_tiempo_real as _leer_rt
                import time as _time
                total_lecturas = []
                n_snapshots = int(config.get('realtime_snapshots', 5))
                interval = float(config.get('realtime_interval_seconds', 1))
                for i in range(n_snapshots):
                    print(f"  > instantanea {i+1} (stub)...")
                    df_snap = _leer_rt()
                    if not df_snap.empty:
                        total_lecturas.append(df_snap)
                    _time.sleep(interval)
                if total_lecturas:
                    import pandas as _pd
                    almacen_datos['clima'] = _pd.concat(total_lecturas, ignore_index=True)
                else:
                    import pandas as _pd
                    almacen_datos['clima'] = _pd.DataFrame()
                print("Usando stub de prueba para lectura realtime (archivos_test.fuente_realtime)")
            except Exception as exc2:
                print(f"Fallback test stub failed for realtime: {exc2}")
                import pandas as _pd
                almacen_datos['clima'] = _pd.DataFrame()

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
    fintech_path = config.get('fintech_path', 'IA_Proyecto/data/raw/fintech_raw.csv')
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
    import argparse

    parser = argparse.ArgumentParser(description="Run ETL pipeline for selected sources")
    parser.add_argument("--sources", default="all",
                        help="Comma-separated sources: csv,batch,realtime or all (default)")
    parser.add_argument("--config", default="config.json", help="Path to config file")
    args = parser.parse_args()

    selected = set(s.strip() for s in args.sources.split(",") if s.strip())
    if not selected or 'all' in selected:
        results = run_orchestator(args.config)
    else:
        results = run_orchestator_selected(selected, args.config)

