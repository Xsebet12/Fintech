import pandas as pd

def leer_datos_batch(topic: str = 'scifi') -> pd.DataFrame:
    """Stub ligero para `leer_datos_batch` usado solo en pruebas.
    Devuelve un DataFrame pequeño con ejemplos de títulos.
    """
    data = [
        {'book_id': 'b1', 'title': f'{topic} - Ejemplo 1', 'author': 'Autor A'},
        {'book_id': 'b2', 'title': f'{topic} - Ejemplo 2', 'author': 'Autor B'},
    ]
    return pd.DataFrame(data)
