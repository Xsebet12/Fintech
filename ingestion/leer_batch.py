import logging
import os
from typing import Optional

import pandas as pd
import requests

from IA_Proyecto.src.audit_utils import ensure_dir, sha256_text, utc_now_iso

logger = logging.getLogger("ingestion.leer_batch")
def _sha256_bytes(data: bytes) -> str:
def _save_metadata(metadata: dict, source_name: str):
    outdir = ensure_dir(os.path.join("..", "data", "metadata"))
    ts = metadata.get("ingested_at", utc_now_iso())
    safe_ts = ts.replace(":", "").replace(".", "")
    fname = f"ingest_openlibrary_{source_name}_{safe_ts}.json"
    path = os.path.join(outdir, fname)
    try:
        import json

        with open(path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        logger.info(f"Metadata guardada en {path}")
    except Exception as e:
        logger.warning(f"No se pudo guardar metadata: {e}")


def leer_datos_batch(subject: str = "cooking", limit: Optional[int] = 10, timeout: Optional[int] = 10) -> pd.DataFrame:
    """Descarga un batch de OpenLibrary para `subject` con limite `limit`.

    Añade `_ingested_at` y guarda metadata con hash del contenido.
    Retorna DataFrame vacío si la petición falla.
    """
    url = f"https://openlibrary.org/subjects/{subject}.json?limit={limit}"
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        works = data.get("works", [])
        df = pd.json_normalize(works)

        ingested_at = utc_now_iso()
        if not df.empty:
            df["_ingested_at"] = ingested_at
            # generate simple per-row hash if not present
            if "record_hash" not in df.columns:
            df["record_hash"] = df.apply(lambda r: sha256_text("|".join(map(str, r.values))), axis=1)

        # metadata
        metadata = {
            "source": url,
            "subject": subject,
            "ingested_at": ingested_at,
            "records": int(len(df)),
            "response_hash": sha256_text(response.content.decode("utf-8", errors="ignore")),
            "columns": list(df.columns),
        }
        _save_metadata(metadata, subject)

        logger.info(f"Batch pulled {len(df)} records for subject={subject}.")
        return df
    except Exception as e:
        logger.error(f"Error fetching batch from OpenLibrary: {e}")
        return pd.DataFrame()