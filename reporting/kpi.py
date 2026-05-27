from __future__ import annotations

import pandas as pd


def calcular_kpis(almacen_datos: dict) -> pd.DataFrame:
    df_validos = almacen_datos.get('Fintech Validos')
    df_invalidos = almacen_datos.get('Fintech Invalidos')
    df_total = almacen_datos.get('Fintech')

    total_registros = int(len(df_total)) if hasattr(df_total, '__len__') else 0
    registros_validos = int(len(df_validos)) if hasattr(df_validos, '__len__') else 0
    registros_invalidos = int(len(df_invalidos)) if hasattr(df_invalidos, '__len__') else 0
    tasa_validacion = (registros_validos / total_registros) if total_registros else 0.0

    monto_total_valido = 0.0
    monto_promedio_valido = 0.0
    saldo_promedio_final = 0.0
    transacciones_confirmadas = 0
    cuentas_unicas = 0
    meses_unicos = 0

    if isinstance(df_validos, pd.DataFrame) and not df_validos.empty:
        if 'amount' in df_validos.columns:
            monto_total_valido = float(pd.to_numeric(df_validos['amount'], errors='coerce').fillna(0).sum())
            monto_promedio_valido = float(pd.to_numeric(df_validos['amount'], errors='coerce').mean())
        if 'balance_after' in df_validos.columns:
            saldo_promedio_final = float(pd.to_numeric(df_validos['balance_after'], errors='coerce').mean())
        if 'status' in df_validos.columns:
            transacciones_confirmadas = int(df_validos['status'].astype(str).str.upper().eq('COMPLETED').sum())
        if 'account_id' in df_validos.columns:
            cuentas_unicas = int(df_validos['account_id'].nunique(dropna=True))
        if 'reporting_month' in df_validos.columns:
            meses_unicos = int(df_validos['reporting_month'].astype(str).nunique(dropna=True))

    kpis = pd.DataFrame([
        {'kpi': 'total_registros', 'valor': total_registros, 'descripcion': 'Registros totales procesados'},
        {'kpi': 'registros_validos', 'valor': registros_validos, 'descripcion': 'Registros que pasaron validación'},
        {'kpi': 'registros_invalidos', 'valor': registros_invalidos, 'descripcion': 'Registros descartados por validación'},
        {'kpi': 'tasa_registros_validos', 'valor': round(tasa_validacion, 4), 'descripcion': 'Proporción de registros válidos'},
        {'kpi': 'monto_total_valido', 'valor': round(monto_total_valido, 2), 'descripcion': 'Monto total de transacciones válidas'},
        {'kpi': 'monto_promedio_valido', 'valor': round(monto_promedio_valido, 2), 'descripcion': 'Monto promedio de transacciones válidas'},
        {'kpi': 'saldo_promedio_final', 'valor': round(saldo_promedio_final, 2), 'descripcion': 'Saldo promedio posterior a la transacción'},
        {'kpi': 'transacciones_confirmadas', 'valor': transacciones_confirmadas, 'descripcion': 'Cantidad de transacciones con status COMPLETED'},
        {'kpi': 'cuentas_unicas', 'valor': cuentas_unicas, 'descripcion': 'Cantidad de cuentas distintas'},
        {'kpi': 'meses_unicos', 'valor': meses_unicos, 'descripcion': 'Cantidad de meses de reporte distintos'},
    ])

    return kpis
