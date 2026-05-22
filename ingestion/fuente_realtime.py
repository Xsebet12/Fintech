import requests
import pandas as pd
from typing import Optional

def leer_clima_tiempo_real(latitude: Optional[float] = -33.453654,
                            longitude: Optional[float] = -70.573846,
                            timeout: Optional[int] = 5):
    """Consulta Open-Meteo para lat/lon dados y retorna un DataFrame con current_weather.

    Retorna DataFrame vacío en errores.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json().get('current_weather')
        if not data:
            return pd.DataFrame()
        return pd.DataFrame([data])
    except Exception as e:
        print(f"API del clima fallo: {e}")
        return pd.DataFrame()