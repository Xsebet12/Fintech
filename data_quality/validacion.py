import pandas as pd


def _get_setting(config, key, default):
    if isinstance(config, dict):
        return config.get(key, default)
    return default

def ejecutar_validaciones(almacen_datos, config=None):
    print("Validacion de transacciones fintech")
    df = almacen_datos.get('Fintech')
    if df is None or (hasattr(df, 'empty') and df.empty):
        print("No hay datos de fintech para validar.")
    else:
        df = df.copy()
        required_columns = [
            'transaction_id',
            'created_at',
            'reporting_month',
            'account_id',
            'transaction_type',
            'status',
            'amount',
            'balance_before',
            'balance_after',
            'regulatory_code',
            'finalized',
            'record_hash',
            'prev_record_hash',
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Columnas faltantes para validar fintech: {missing_columns}")

        def monto_firmado(tipo, monto):
            if pd.isna(monto):
                return pd.NA
            tipo = str(tipo).strip().upper()
            if tipo in {'DEBIT', 'FEE'}:
                return -abs(float(monto))
            return abs(float(monto))

        if 'transaction_type' in df.columns and 'amount' in df.columns:
            df['monto_firmado'] = [monto_firmado(tipo, monto) for tipo, monto in zip(df['transaction_type'], df['amount'])]
        else:
            df['monto_firmado'] = pd.NA

        if 'status' in df.columns:
            status_upper = df['status'].astype(str).str.strip().str.upper()
            df['val_status_known'] = status_upper.isin({'COMPLETED', 'FAILED', 'PENDING'})
            if {'balance_before', 'balance_after'}.issubset(df.columns):
                df['val_status_integrity'] = ~((status_upper == 'FAILED') & (df['balance_before'] != df['balance_after']))
            else:
                df['val_status_integrity'] = False
            df['val_status'] = df['val_status_known'] & df['val_status_integrity']
        else:
            status_upper = pd.Series('', index=df.index)
            df['val_status_known'] = False
            df['val_status_integrity'] = False
            df['val_status'] = False

        validation_config = _get_setting(config, 'validation', {})
        tolerance = float(_get_setting(validation_config, 'balance_tolerance', 0.01))
        if 'balance_before' in df.columns and 'balance_after' in df.columns and 'monto_firmado' in df.columns:
            df['val_balance'] = False
            completed_mask = status_upper.eq('COMPLETED')
            failed_or_pending_mask = status_upper.isin({'FAILED', 'PENDING'})

            if completed_mask.any():
                df.loc[completed_mask, 'val_balance'] = (
                    (df.loc[completed_mask, 'balance_before'] + df.loc[completed_mask, 'monto_firmado'])
                    .sub(df.loc[completed_mask, 'balance_after'])
                    .abs()
                    <= tolerance
                )

            if failed_or_pending_mask.any():
                df.loc[failed_or_pending_mask, 'val_balance'] = (
                    df.loc[failed_or_pending_mask, 'balance_before']
                    .sub(df.loc[failed_or_pending_mask, 'balance_after'])
                    .abs()
                    <= tolerance
                )
        else:
            df['val_balance'] = False

        if {'created_at', 'reporting_month'}.issubset(df.columns):
            created_at = pd.to_datetime(df['created_at'], errors='coerce', utc=True)
            df['val_reporting_month'] = created_at.dt.strftime('%Y-%m') == df['reporting_month'].astype(str).str.strip()
        else:
            df['val_reporting_month'] = False

        if 'amount' in df.columns:
            df['val_amount'] = pd.to_numeric(df['amount'], errors='coerce').gt(0)
        else:
            df['val_amount'] = False

        if 'record_hash' in df.columns and 'prev_record_hash' in df.columns:
            df['val_hash_present'] = df['record_hash'].astype(str).str.strip().ne('') & df['prev_record_hash'].astype(str).str.strip().ne('')
        else:
            df['val_hash_present'] = False

        if {'created_at', 'record_hash', 'prev_record_hash'}.issubset(df.columns):
            ordered = df.copy()
            ordered['_sort_created_at'] = pd.to_datetime(ordered['created_at'], errors='coerce', utc=True)
            ordered = ordered.sort_values(['_sort_created_at', 'transaction_id'], na_position='last')
            zero_hash = _get_setting(validation_config, 'zero_hash', '0000000000000000000000000000000000000000000000000000000000000000')

            expected_prev_hash = ordered['record_hash'].fillna('').astype(str).str.strip().shift(1, fill_value=zero_hash)
            current_prev_hash = ordered['prev_record_hash'].fillna('').astype(str).str.strip()
            current_record_hash = ordered['record_hash'].fillna('').astype(str).str.strip()

            ordered['val_hash_chain'] = current_prev_hash.eq(expected_prev_hash) & current_record_hash.ne('')

            df['val_hash_chain'] = False
            df.loc[ordered.index, 'val_hash_chain'] = ordered['val_hash_chain']
        else:
            df['val_hash_chain'] = False

        if 'transaction_id' in df.columns:
            df['val_unique_id'] = ~df['transaction_id'].duplicated(keep=False)
        else:
            df['val_unique_id'] = False

        columnas_validacion = [col for col in ['val_amount', 'val_status', 'val_balance', 'val_reporting_month', 'val_hash_present', 'val_hash_chain', 'val_unique_id'] if col in df.columns]
        if columnas_validacion:
            df['registro_valido'] = df[columnas_validacion].all(axis=1)
        else:
            df['registro_valido'] = False

        def obtener_observaciones(row):
            errores = []
            if not row.get('val_amount', False):
                errores.append('Monto inválido')
            if not row.get('val_status', False):
                errores.append('Estado no permitido o inconsistente')
            if not row.get('val_balance', False):
                errores.append('Saldo inconsistente')
            if not row.get('val_reporting_month', False):
                errores.append('Mes de reporte no coincide con created_at')
            if not row.get('val_hash_present', False):
                errores.append('Hashes ausentes o vacíos')
            if not row.get('val_hash_chain', False):
                errores.append('Cadena de hashes inválida')
            if not row.get('val_unique_id', False):
                errores.append('transaction_id duplicado')
            return ' | '.join(errores) if errores else 'Registro válido'

        df['observaciones'] = df.apply(obtener_observaciones, axis=1)

        df_validos = df[df['registro_valido']].copy()
        df_invalidos = df[~df['registro_valido']].copy()

        almacen_datos['Fintech'] = df
        almacen_datos['Fintech Validos'] = df_validos
        almacen_datos['Fintech Invalidos'] = df_invalidos
        print(f"Validación fintech completada: {len(df_validos)} válidos y {len(df_invalidos)} inválidos.")

    return(almacen_datos)