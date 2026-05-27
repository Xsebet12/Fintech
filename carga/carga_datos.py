from __future__ import annotations

from pathlib import Path

import pandas as pd

from IA_Proyecto.src.audit_utils import ensure_dir, save_dataframe_versioned, utc_now_iso


def cargar_datos(almacen_datos: dict, kpi_df: pd.DataFrame, output_dirs: dict | None = None) -> dict:
    output_dirs = output_dirs or {}
    processed_dir = ensure_dir(output_dirs.get('processed', 'IA_Proyecto/data/processed'))
    kpi_dir = ensure_dir(output_dirs.get('kpi', 'IA_Proyecto/data/kpi'))

    resultados = {}

    df_validos = almacen_datos.get('Fintech Validos')
    if isinstance(df_validos, pd.DataFrame) and not df_validos.empty:
        resultados['Fintech Validos'] = save_dataframe_versioned(
            df_validos,
            processed_dir,
            'fintech_limpio',
            metadata={
                'source': 'Fintech Validos',
                'saved_at': utc_now_iso(),
            },
        )

    df_invalidos = almacen_datos.get('Fintech Invalidos')
    if isinstance(df_invalidos, pd.DataFrame) and not df_invalidos.empty:
        resultados['Fintech Invalidos'] = save_dataframe_versioned(
            df_invalidos,
            processed_dir,
            'fintech_invalidos',
            metadata={
                'source': 'Fintech Invalidos',
                'saved_at': utc_now_iso(),
            },
        )

    if isinstance(kpi_df, pd.DataFrame) and not kpi_df.empty:
        resultados['KPI'] = save_dataframe_versioned(
            kpi_df,
            kpi_dir,
            'kpi_fintech',
            metadata={
                'source': 'KPI Fintech',
                'saved_at': utc_now_iso(),
            },
        )

    return resultados
