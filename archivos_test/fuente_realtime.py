import pandas as pd
from datetime import datetime

def leer_clima_tiempo_real() -> pd.DataFrame:
    """Stub ligero para `leer_clima_tiempo_real` usado solo en pruebas.
    Devuelve un snapshot con marca temporal y temperatura simulada.
    """
    data = [{
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'temperature_c': 20.0,
        'humidity_pct': 50,
        'source': 'stub'
    }]
    return pd.DataFrame(data)
