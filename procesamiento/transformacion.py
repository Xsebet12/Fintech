import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, KBinsDiscretizer

def generar_transformaciones(almacen_datos):

    print("\n--- Ejecutando transformaciones en procesamiento/transformacion.py")

    df = almacen_datos.get('Titanic')
    if df is None or (hasattr(df, 'empty') and df.empty):
        print("No hay datos del Titanic para transformar.")
        return almacen_datos

    # Detectar nombre de columna para sobrevivencia con tolerancia a typos
    possible_survived = [c for c in df.columns if c.lower() in ('survived', '2urvived', 'surv')]
    if possible_survived:
        surv_col = possible_survived[0]
        resumen_supervivencia = df.groupby(surv_col).size()
        almacen_datos['Resumen_Supervivencia'] = resumen_supervivencia
        print(f"Entrada 'Resumen_Supervivencia' agregada correctamente usando columna '{surv_col}'.")
    else:
        print("Advertencia: No se encontró columna de supervivencia conocida ('Survived'). Omite resumen.")

    if 'Age' in df.columns:
        scaler = MinMaxScaler()
        df['Age'] = df['Age'].fillna(df['Age'].median())
        df['Age'] = scaler.fit_transform(df[['Age']])
        print("Columna 'Age' normalizada (0-1).")
    
    if 'Fare' in df.columns:
        df['Fare'] = df['Fare'].fillna(df['Fare'].median())
        def categorizar_fare(valor):
            try:
                if valor <= 50: return "0-50 dolares"
                elif valor <= 100: return "51-100 dolares"
                else: return "más de 100 dolares"
            except Exception:
                return "desconocido"
        df['Fare_Category'] = df['Fare'].apply(categorizar_fare)
        print("Columna 'Fare_Category' creada.")
    
    # Actualizar el dataframe en el almacén
    almacen_datos['Titanic'] = df

    return almacen_datos
