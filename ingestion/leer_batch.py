import pandas as pd
import requests
from typing import Optional

def leer_datos_batch(subject: str = 'cooking', limit: Optional[int] = 10, timeout: Optional[int] = 10):
    """Descarga un batch de OpenLibrary para `subject` con limite `limit`.

    Retorna DataFrame vacío si la petición falla.
    """
    url = f"https://openlibrary.org/subjects/{subject}.json?limit={limit}"
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        works = data.get('works', [])
        df = pd.json_normalize(works)
        cols = [c for c in ['title', 'key', 'first_publish_year'] if c in df.columns]
        df = df[cols] if cols else df
        print(f"Batch pulled {len(df)} book records for subject={subject}.")
        return df
    except Exception as e:
        print(f"Error fetching batch from OpenLibrary: {e}")
        return pd.DataFrame()