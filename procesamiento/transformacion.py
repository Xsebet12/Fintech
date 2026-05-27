import pandas as pd

def generar_transformaciones(almacen_datos):

    print("\n--- Ejecutando transformaciones en procesamiento/transformacion.py")

    df = almacen_datos.get('Fintech')
    if df is None or (hasattr(df, 'empty') and df.empty):
        print("No hay datos de fintech para transformar.")
        return almacen_datos

    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]

    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce', utc=True)

    if 'transaction_id' in df.columns:
        df['transaction_id'] = df['transaction_id'].astype(str).str.strip()

    if 'account_id' in df.columns:
        df['account_id'] = df['account_id'].astype(str).str.strip()

    if 'status' in df.columns:
        df['status'] = df['status'].astype(str).str.strip().str.upper()

    if 'reporting_month' in df.columns:
        df['reporting_month'] = df['reporting_month'].astype(str).str.strip()

    numeric_columns = ['amount', 'balance_before', 'balance_after']
    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors='coerce')

    if 'finalized' in df.columns:
        def normalizar_booleano(valor):
            if pd.isna(valor):
                return False
            if isinstance(valor, bool):
                return valor
            return str(valor).strip().lower() in {'true', '1', 'yes', 'y', 'si', 'sí'}

        df['finalized'] = df['finalized'].apply(normalizar_booleano)

    if 'transaction_type' in df.columns and 'amount' in df.columns:
        def monto_firmado(row):
            tipo = str(row.get('transaction_type', '')).strip().upper()
            monto = row.get('amount')
            if pd.isna(monto):
                return pd.NA
            if tipo in {'DEBIT', 'FEE'}:
                return -abs(monto)
            return abs(monto)

        df['amount_signed'] = df.apply(monto_firmado, axis=1)

    if 'balance_before' in df.columns and 'balance_after' in df.columns:
        df['balance_delta'] = df['balance_after'] - df['balance_before']

    if 'metadata' in df.columns:
        df['metadata_channel'] = df['metadata'].astype(str).str.extract(r'channel=([^|]+)', expand=False).str.strip()
        df['metadata_note'] = df['metadata'].astype(str).str.extract(r'note=([^|]+)', expand=False).str.strip()

    if 'created_at' in df.columns:
        df['created_date'] = df['created_at'].dt.date
        df['created_month'] = df['created_at'].dt.strftime('%Y-%m')

    if {'reporting_month', 'transaction_type', 'amount'}.issubset(df.columns):
        resumen_mensual = (
            df.groupby(['reporting_month', 'transaction_type'], dropna=False)
            .agg(
                total_transacciones=('transaction_id', 'count') if 'transaction_id' in df.columns else ('amount', 'count'),
                monto_total=('amount', 'sum'),
            )
            .reset_index()
        )
        almacen_datos['Resumen_Mensual'] = resumen_mensual
        print("Resumen_Mensual agregado correctamente.")

    if {'account_id', 'amount', 'status'}.issubset(df.columns):
        resumen_cuentas = (
            df.groupby('account_id', dropna=False)
            .agg(
                transacciones=('transaction_id', 'count') if 'transaction_id' in df.columns else ('amount', 'count'),
                monto_total=('amount', 'sum'),
                monto_promedio=('amount', 'mean'),
                transacciones_confirmadas=('status', lambda s: (s == 'CONFIRMED').sum()),
            )
            .reset_index()
            .sort_values('monto_total', ascending=False)
        )
        almacen_datos['Resumen_Cuentas'] = resumen_cuentas
        print("Resumen_Cuentas agregado correctamente.")
    
    almacen_datos['Fintech'] = df

    return almacen_datos
