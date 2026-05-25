import logging
import os
from typing import Optional

import pandas as pd

from IA_Proyecto.src.audit_utils import ensure_dir, sha256_file, sha256_text, utc_now_iso

logger = logging.getLogger("ingestion.leer_csv")


def _row_hash(row: pd.Series) -> str:
    # Concatenate string values deterministically
    return sha256_text("|".join([str(v) for v in row.values]))


def _save_metadata(metadata: dict, source: str):
    outdir = ensure_dir(os.path.join(os.path.dirname(source), "..", "data", "metadata"))
    ts = metadata.get("ingested_at", utc_now_iso())
    safe_ts = ts.replace(":", "").replace(".", "")
    fname = f"ingest_{os.path.basename(source)}_{safe_ts}.json"
    path = os.path.join(outdir, fname)
    try:
        import json

        with open(path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        logger.info(f"Metadata guardada en {path}")
    except Exception as e:
        logger.warning(f"No se pudo guardar metadata: {e}")


def leer_datos_csv(path: Optional[str] = None, save_metadata: bool = True) -> pd.DataFrame:
    """Lee un CSV desde `path`. Si `path` es None usa 'fintech.csv'.

    Añade columna `_ingested_at` con timestamp UTC y genera `record_hash`
    si falta o es nulo. Guarda un archivo JSON con metadatos de la ingesta.

    Retorna DataFrame vacío si el archivo no existe.
    """
    source = path or "fintech.csv"

    if not os.path.exists(source):
        logger.warning(f"Archivo no encontrado: {source} — devolviendo DataFrame vacío")
        return pd.DataFrame()

    try:
        df = pd.read_csv(source)
    except Exception as e:
        logger.error(f"Error leyendo CSV {source}: {e}")
        return pd.DataFrame()

    ingested_at = utc_now_iso()
    df["_ingested_at"] = ingested_at

    # Asegurar que exista columna record_hash
    if "record_hash" not in df.columns:
        logger.info("Columna 'record_hash' ausente: generando hashes por fila.")
        df["record_hash"] = df.apply(_row_hash, axis=1)
    else:
        # llenar hashes faltantes
        missing = df["record_hash"].isnull() | (df["record_hash"].astype(str).str.strip() == "")
        if missing.any():
            logger.info(f"{missing.sum()} registros sin 'record_hash', generando.")
            df.loc[missing, "record_hash"] = df[missing].apply(_row_hash, axis=1)

    # Guardar metadata sobre la ingesta
    if save_metadata:
        metadata = {
            "source": source,
            "ingested_at": ingested_at,
            "records": int(len(df)),
            "file_hash": sha256_file(source),
            "columns": list(df.columns),
        }
        _save_metadata(metadata, source)

    logger.info(f"Total lineas importadas: {len(df)} from {source}")
    return df
