import pandas as pd
import os
from typing import Optional

def leer_datos_csv(path: Optional[str] = None):
    """Lee un CSV desde `path`. Si `path` es None usa 'Titanic.csv'.

    Devuelve un DataFrame vacío si el archivo no existe.
    """
    source = path or "Titanic.csv"
    if not os.path.exists(source):
        print(f'Archivo no encontrado: {source} — devolviendo DataFrame vacío')
        return pd.DataFrame()
    df = pd.read_csv(source)
    print(f'total lineas importadas:  {len(df)} from {source}')
    return df