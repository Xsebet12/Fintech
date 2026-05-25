import logging
import os
from typing import Optional

import pandas as pd
import requests

from IA_Proyecto.src.audit_utils import ensure_dir, sha256_text, utc_now_iso

logger = logging.getLogger("ingestion.fuente_realtime")
def _save_metadata(metadata: dict, name: str = "open-meteo"):
    outdir = ensure_dir(os.path.join("..", "data", "metadata"))
    ts = metadata.get("ingested_at", utc_now_iso())
    safe_ts = ts.replace(":", "").replace(".", "")
    fname = f"ingest_{name}_{safe_ts}.json"
    path = os.path.join(outdir, fname)
    try:
        import json

        with open(path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        logger.info(f"Metadata guardada en {path}")
    except Exception as e:
        logger.warning(f"No se pudo guardar metadata: {e}")


def leer_clima_tiempo_real(latitude: Optional[float] = -33.453654,
                            longitude: Optional[float] = -70.573846,
                            timeout: Optional[int] = 5) -> pd.DataFrame:
    """Consulta Open-Meteo para lat/lon dados y retorna un DataFrame con current_weather.

    Retorna DataFrame vacío en errores. Guarda metadata con hash de respuesta.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json().get("current_weather")
        if not data:
            return pd.DataFrame()

        ingested_at = utc_now_iso()
        df = pd.DataFrame([data])
        df["_ingested_at"] = ingested_at

        metadata = {
            "source": url,
            "ingested_at": ingested_at,
            "records": int(len(df)),
            "response_hash": sha256_text(response.content.decode("utf-8", errors="ignore")),
            "columns": list(df.columns),
        }
        _save_metadata(metadata)

        return df
    except Exception as e:
        logger.error(f"API del clima fallo: {e}")
        return pd.DataFrame()