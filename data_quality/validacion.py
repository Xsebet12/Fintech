import pandas as pd
import re

def ejecutar_validaciones(almacen_datos):
    print("Validacion de registros de sobrevivientes")
    df = almacen_datos.get('Titanic')
    if df is None or (hasattr(df, 'empty') and df.empty):
        print("No hay datos de Titanic para validar.")
    else:
        possible_survived = [c for c in df.columns if c.lower() in ('survived', '2urvived', 'surv')]
        if possible_survived and 'Pclass' in df.columns:
            surv_col = possible_survived[0]
            sobrevivientes = (df[surv_col] == 1) & (df['Pclass'].notna())
            df_sobrevivientes = df[sobrevivientes].copy()
            almacen_datos['registro sobrevivientes'] = df_sobrevivientes
            print(f"Validacion exitosa de sobrevivientes usando columna '{surv_col}'")
        else:
            print("No se pudo validar sobrevivientes: faltan columnas esperadas ('Survived'/'Pclass').")

    if 'Libros' in almacen_datos and not almacen_datos['Libros'].empty:
        df_libros = almacen_datos['Libros']
        
        # Función para detectar si un texto contiene solo caracteres latinos
        # Permite letras (a-z, A-Z), números, espacios y signos de puntuación comunes
        def es_latino(texto):
            if pd.isna(texto): return False
            # Regex que busca caracteres NO latinos/estándar
            return bool(re.match(r'^[a-zA-Z0-9\s\.,!\?\-\(\)áéíóúÁÉÍÓÚñÑ]+$', str(texto)))

        # Aplicamos el filtro a la columna de títulos
        col_titulo = 'title' if 'title' in df_libros.columns else (df_libros.columns[0] if len(df_libros.columns) else None)
        if col_titulo is None:
            print("No hay columna de títulos en Libros para validar.")
        else:
            mascara_latina = df_libros[col_titulo].apply(es_latino)
        df_libros_al = df_libros[mascara_latina].copy()
        
        almacen_datos['Libros AL'] = df_libros_al
        print(f"Validación Libros exitosa: {len(df_libros_al)} libros con alfabeto latino.")

    return(almacen_datos)