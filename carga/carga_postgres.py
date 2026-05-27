from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


TRANSACTION_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS ventas_clean (
    transaction_id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL,
    reporting_month TEXT NOT NULL,
    account_id TEXT NOT NULL,
    counterparty_account TEXT NULL,
    transaction_group_id TEXT NULL,
    transaction_type TEXT NOT NULL,
    status TEXT NOT NULL,
    amount NUMERIC(18,2) NOT NULL,
    currency TEXT NOT NULL,
    balance_before NUMERIC(18,2) NOT NULL,
    balance_after NUMERIC(18,2) NOT NULL,
    regulatory_code TEXT NULL,
    finalized BOOLEAN NOT NULL,
    record_hash TEXT NOT NULL,
    prev_record_hash TEXT NOT NULL,
    metadata TEXT NULL,
    _ingested_at TIMESTAMPTZ NULL,
    amount_signed NUMERIC(18,2) NULL,
    balance_delta NUMERIC(18,2) NULL,
    metadata_channel TEXT NULL,
    metadata_note TEXT NULL,
    created_date DATE NULL,
    created_month TEXT NULL
);
"""

INVALID_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS ventas_error (
    transaction_id TEXT,
    created_at TIMESTAMPTZ NULL,
    reporting_month TEXT NULL,
    account_id TEXT NULL,
    counterparty_account TEXT NULL,
    transaction_group_id TEXT NULL,
    transaction_type TEXT NULL,
    status TEXT NULL,
    amount NUMERIC(18,2) NULL,
    currency TEXT NULL,
    balance_before NUMERIC(18,2) NULL,
    balance_after NUMERIC(18,2) NULL,
    regulatory_code TEXT NULL,
    finalized BOOLEAN NULL,
    record_hash TEXT NULL,
    prev_record_hash TEXT NULL,
    metadata TEXT NULL,
    _ingested_at TIMESTAMPTZ NULL,
    amount_signed NUMERIC(18,2) NULL,
    balance_delta NUMERIC(18,2) NULL,
    metadata_channel TEXT NULL,
    metadata_note TEXT NULL,
    created_date DATE NULL,
    created_month TEXT NULL,
    val_amount BOOLEAN NULL,
    val_balance BOOLEAN NULL,
    val_reporting_month BOOLEAN NULL,
    val_hash_present BOOLEAN NULL,
    val_hash_chain BOOLEAN NULL,
    val_unique_id BOOLEAN NULL,
    registro_valido BOOLEAN NULL,
    observaciones TEXT NULL
);
"""

KPI_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS kpi_fintech (
    kpi TEXT,
    valor NUMERIC(18,4),
    descripcion TEXT
);
"""


def _build_connection_string() -> str:
    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / "db.env")

    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")

    missing = [
        name
        for name, value in {
            "DB_HOST": db_host,
            "DB_PORT": db_port,
            "DB_NAME": db_name,
            "DB_USER": db_user,
            "DB_PASSWORD": db_password,
        }.items()
        if not value
    ]
    if missing:
        raise ValueError(
            "Faltan variables de conexión en db.env: " + ", ".join(missing)
        )

    return f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def load_to_postgres(
    almacen_datos: dict[str, Any],
    kpi_df: pd.DataFrame,
    *,
    clear_first: bool = True,
) -> dict[str, int]:
    df_validos = almacen_datos.get("Fintech Validos")
    df_invalidos = almacen_datos.get("Fintech Invalidos")

    if not isinstance(df_validos, pd.DataFrame) or df_validos.empty:
        raise ValueError("No hay datos válidos para cargar en PostgreSQL")
    if not isinstance(df_invalidos, pd.DataFrame):
        raise ValueError("No hay datos inválidos válidos para cargar en PostgreSQL")
    if not isinstance(kpi_df, pd.DataFrame) or kpi_df.empty:
        raise ValueError("No hay KPIs para cargar en PostgreSQL")

    engine = create_engine(_build_connection_string())

    clean_df = df_validos.copy()
    invalid_df = df_invalidos.copy()
    kpi_out = kpi_df.copy()

    with engine.begin() as conn:
        conn.execute(text(TRANSACTION_TABLE_SQL))
        conn.execute(text(INVALID_TABLE_SQL))
        conn.execute(text(KPI_TABLE_SQL))

        if clear_first:
            conn.execute(text("TRUNCATE TABLE ventas_clean, ventas_error, kpi_fintech;"))

        clean_df.to_sql("ventas_clean", conn, if_exists="append", index=False, method="multi", chunksize=1000)
        invalid_df.to_sql("ventas_error", conn, if_exists="append", index=False, method="multi", chunksize=1000)
        kpi_out.to_sql("kpi_fintech", conn, if_exists="append", index=False, method="multi", chunksize=1000)

    return {
        "ventas_clean": int(len(clean_df)),
        "ventas_error": int(len(invalid_df)),
        "kpi_fintech": int(len(kpi_out)),
    }
